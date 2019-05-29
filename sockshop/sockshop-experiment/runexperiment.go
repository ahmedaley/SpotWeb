package main

import (
	"bytes"
	"fmt"
	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/client"
	"github.com/libvirt/libvirt-go"
	"context"
	"io/ioutil"
	"log"
	"os/exec"
	"path"
	"strings"
	"time"
	"strconv"
	"encoding/json"
	"os"
	"io"
)

var retryTimes = 6
var retryIntervalInSeconds = 10
var c Config

func cleanUpExistingDomains(conn *libvirt.Connect) {
	fmt.Println("Cleaning up existing domains")
	for _, vm := range c.VMs {
		domain, err := conn.LookupDomainByName(vm.Name)
		if err != nil {
			lverr, ok := err.(libvirt.Error)
			if ok && lverr.Code == libvirt.ERR_NO_DOMAIN {
				// domain not found, continue
				continue
			} else {
				log.Fatal("Error:", err)
			}
		}
		// domain found, destroy it
		fmt.Printf("Domain %s found, trying to destroy...\n", vm.Name)
		checkErr(domain.Destroy())
	}

	for _, vm := range c.VMs {
		for {
			_, err := conn.LookupDomainByName(vm.Name)
			if err != nil {
				lverr, ok := err.(libvirt.Error)
				if ok && lverr.Code == libvirt.ERR_NO_DOMAIN {
					break;
				} else {
					log.Fatal("Error:", err)
				}
			} else {
				time.Sleep(time.Duration(1) * time.Second)
			}
		}
	}
}

func checkDomainsAreRunning(configs map[string]VMConfig) {
	for _, vm := range c.VMs {
		success_flag := false
		for i := 0; i < retryTimes; i++ {
			cmd := exec.Command("ssh", "-o", "StrictHostKeyChecking=no", "ubuntu@"+configs[vm.Name].Address, "date")
			var outBuffer bytes.Buffer
			var errBuffer bytes.Buffer
			cmd.Stdout = &outBuffer
			cmd.Stderr = &errBuffer
			err := cmd.Run()
			if err != nil {
				fmt.Println(errBuffer.String())
				fmt.Printf("ssh to domain %s failed, retrying...\n", vm.Name)
				time.Sleep(time.Duration(retryIntervalInSeconds) * time.Second)
			} else {
				fmt.Printf("Domain %s up and running: %s", vm.Name, outBuffer.String())
				success_flag = true
				break
			}
		}
		if success_flag != true {
			log.Fatalf("Domain %s starting timeout\n", vm.Name)
		}
	}
}

func runCommandOverSSH(command string, address string) string {
	cmd := exec.Command("ssh", "-o", "StrictHostKeyChecking=no", "ubuntu@"+address, command)
	var outBuffer, errBuffer bytes.Buffer
	cmd.Stdout = &outBuffer
	cmd.Stderr = &errBuffer
	err := cmd.Run()
	if err != nil {
		log.Fatal(err, cmd, address, errBuffer.String())
	}
	return outBuffer.String()
}

func startLoadTestContainer(host string, clientNum int, requestNum int) string {
	cli, err := client.NewClientWithOpts()
	checkErr(err)

	ctx := context.Background()
	args := []string{"-h", host, "-c", strconv.Itoa(clientNum), "-r", strconv.Itoa(requestNum)}
	resp, err := cli.ContainerCreate(ctx, &container.Config{
		Image: "weaveworksdemos/load-test",
		Cmd:   args,
		AttachStderr: true,
		AttachStdout: true,
		Tty: true}, nil, nil, "")
	checkErr(err)

	checkErr(cli.ContainerStart(ctx, resp.ID, types.ContainerStartOptions{}))
	return resp.ID
}

func main() {
	conn, err := libvirt.NewConnect("qemu:///system")
	checkErr(err)
	defer conn.Close()

	c.LoadFromFile("conf.yml")

	cleanUpExistingDomains(conn)

	var domains map[string]*libvirt.Domain
	domains = make(map[string]*libvirt.Domain)
	for _, vm := range c.VMs {
		vmDomainXMLPath := path.Join(c.BasePath, vm.Name+".xml")
		vmDomainXMLByteArray, err := ioutil.ReadFile(vmDomainXMLPath)
		checkErr(err)
		domains[vm.Name], err = conn.DomainCreateXML(string(vmDomainXMLByteArray), 0)
		// domains[vm.Name], err = conn.DomainCreateXML(string(vmDomainXMLByteArray), libvirt.DOMAIN_START_AUTODESTROY)
		checkErr(err)
	}

	var configs map[string]VMConfig
	configs = make(map[string]VMConfig)
	for _, vm := range c.VMs {
		configs[vm.Name] = vm
	}

	checkDomainsAreRunning(configs)

	// init docker swarm
	dockerSwarmInitOut := runCommandOverSSH("docker swarm init", configs["manager"].Address)
	for _, line := range strings.Split(dockerSwarmInitOut, "\n") {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "docker swarm join --token") {
			fmt.Println("application:")
			fmt.Println(runCommandOverSSH(line, configs["application"].Address))

			fmt.Println("database:")
			fmt.Println(runCommandOverSSH(line, configs["database"].Address))
			break
		}
	}

	fmt.Println("manager:")
	fmt.Println(runCommandOverSSH("docker node update --label-add role=application application", configs["manager"].Address))
	fmt.Println(runCommandOverSSH("docker node update --label-add role=database database", configs["manager"].Address))

	fmt.Println(runCommandOverSSH("docker service create --name registry --publish published=5000,target=5000 registry:2", configs["manager"].Address))
	fmt.Println(runCommandOverSSH("cd microservices-demo/deploy/docker-swarm/ && docker-compose push", configs["manager"].Address))
	fmt.Println(runCommandOverSSH("cd microservices-demo/deploy/docker-swarm/ && docker stack deploy --compose-file docker-compose.yml sockshop", configs["manager"].Address))

	fmt.Println("Waiting for sockshop to start...")
	for {
		cmd := exec.Command("curl", configs["application"].Address+"/catalogue")
		var out bytes.Buffer
		cmd.Stdout = &out
		if err := cmd.Run(); err != nil {
			time.Sleep(time.Duration(1) * time.Second)
			continue
		}
		if strings.Contains(out.String(), "error") {
			time.Sleep(time.Duration(1) * time.Second)
			continue
		}
		fmt.Println(out.String())
		break
	}

	fmt.Println("Starting load test")
	// start load test container

	containerID := startLoadTestContainer(configs["application"].Address, c.ClientNum, c.RequestNum)

	cli, err := client.NewClientWithOpts()
	checkErr(err)
	ctx := context.Background()

	var statsOutputBuffer bytes.Buffer
	for {
		// record current time
		statsOutputBuffer.WriteString(strconv.FormatInt(time.Now().UnixNano(), 10))
		statsOutputBuffer.WriteString("\n")

		// record cpu stats and memory stats
		for domainName, domain := range domains {
			cpuStats, err := domain.GetCPUStats(-1, 1, 0)
			checkErr(err)
			memoryStats, err := domain.MemoryStats(uint32(libvirt.DOMAIN_MEMORY_STAT_NR), 0)
			checkErr(err)
			statsOutputBuffer.WriteString(domainName)
			statsOutputBuffer.WriteString("\t")

			out, err := json.Marshal(cpuStats)
			checkErr(err)

			statsOutputBuffer.WriteString(string(out))
			statsOutputBuffer.WriteString("\t")

			out, err = json.Marshal(memoryStats)
			checkErr(err)
			statsOutputBuffer.WriteString(string(out))
			statsOutputBuffer.WriteString("\n")
		}


		containerJson, err := cli.ContainerInspect(ctx, containerID)
		checkErr(err)
		// check if the load test container has stopped
		if containerJson.State.Running == false {
			break
		}

		time.Sleep(time.Duration(1) * time.Second)
	}

	statsOutputFile, err := os.Create("stats.out")
	checkErr(err)
	statsOutputFile.Write(statsOutputBuffer.Bytes())
	statsOutputFile.Close()

	dockerOutputFile, err := os.Create("docker.out")
	checkErr(err)
	reader, err := cli.ContainerLogs(ctx, containerID, types.ContainerLogsOptions{ShowStderr: true, ShowStdout: true, Follow: true})
	defer reader.Close()
	io.Copy(dockerOutputFile, reader)
	dockerOutputFile.Close()
}
