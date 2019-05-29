package main

import (
	"fmt"
	"os"
	"path"
	"text/template"
	"os/exec"
)



func preProcess(config Config) {
	checkErr(os.RemoveAll(config.BasePath))
	checkErr(os.Mkdir(config.BasePath, 0755))

	for _, vm := range config.VMs {
		vmFolder := path.Join(config.BasePath, vm.Name)
		checkErr(os.Mkdir(vmFolder, 0755))

		// Create vm image
		vm.SystemDiskFilePath = path.Join(vmFolder, vm.Name+".qcow2")
		cmd := exec.Command("qemu-img", "create", "-f", "qcow2", "-b", config.BaseImg, vm.SystemDiskFilePath)
		checkErr(cmd.Run())

		// Create network configuration
		netConfigFilePath := path.Join(vmFolder, "network_config.yml")
		netConfigFile, err := os.OpenFile(netConfigFilePath, os.O_CREATE|os.O_WRONLY, 0644)
		checkErr(err)
		tmpl, err := template.ParseFiles("network_config_template.yml",)
		tmpl.Execute(netConfigFile, vm)
		netConfigFile.Close()

		// Create user data configuration
		userDataConfigFilePath := path.Join(vmFolder, "user_data.yml")
		userDataConfigFile, err := os.OpenFile(userDataConfigFilePath, os.O_CREATE|os.O_WRONLY, 0644)
		checkErr(err)
		tmpl, err = template.ParseFiles("user_data_template.yml",)
		tmpl.Execute(userDataConfigFile, vm)
		userDataConfigFile.Close()


		// Create user data disk
		vm.UserDataDiskFilePath = path.Join(vmFolder, vm.Name+"_user_data.img")
		cmd = exec.Command("cloud-localds","-N", netConfigFilePath, vm.UserDataDiskFilePath, userDataConfigFilePath)
		checkErr(cmd.Run())

		// Create domain.xml
		tmpl, err = template.ParseFiles("domain_template.xml",)
		checkErr(err)
		domainfilePath := path.Join(config.BasePath, vm.Name+".xml")
		domainFile, err := os.OpenFile(domainfilePath, os.O_CREATE|os.O_WRONLY, 0644)
		checkErr(err)
		tmpl.Execute(domainFile, vm)
		domainFile.Close()
	}
}

func main() {
	var c Config
	c.LoadFromFile("conf.yml")
	fmt.Println(c)
	preProcess(c)
}
