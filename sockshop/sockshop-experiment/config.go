package main

import (
	"log"
	"io/ioutil"
	"gopkg.in/yaml.v2"
)

type VMConfig struct {
	Name                 string
	Memory               int32
	Vcpu                 int32
	Address              string
	SystemDiskFilePath   string
	UserDataDiskFilePath string
}

type Config struct {
	BaseImg    string     `yaml:"baseImg"`
	BasePath   string     `yaml:"basePath"`
	ClientNum  int        `yaml:"clientNum"`
	RequestNum int      `yaml:"requestNum"`
	VMs        []VMConfig `yaml:"VMs"`
}

func checkErr(err error) {
	if err != nil {
		log.Fatal("Error:", err)
	}
}

func (c *Config) LoadFromFile(configFile string) *Config {
	yamlFile, err := ioutil.ReadFile(configFile)
	checkErr(err)

	checkErr(yaml.Unmarshal(yamlFile, c))

	return c
}
