package edu.umass.binwang.slate

import spark.Spark
import com.google.gson.Gson
import com.google.gson.annotations.SerializedName
import java.io.File
import java.util.concurrent.TimeUnit
import kotlin.system.exitProcess

const val TEMPLATE_RESOURCE = "haproxy-template.cfg"
const val CONTAINER_NAME = "haproxy"

class Server(@SerializedName("Name") val name: String,
             @SerializedName("Endpoint") val endpoint: String,
             @SerializedName("Weight") val weight: Int) {
    override fun toString(): String {
        val stringBuilder = StringBuilder()
        stringBuilder.append(name)
        stringBuilder.append("\t")
        stringBuilder.append(endpoint)
        stringBuilder.append("\t")
        stringBuilder.append(weight)
        return stringBuilder.toString()
    }
}

class Config(@SerializedName("Backend") val backend: Array<Server>) {
    override fun toString(): String {
        return backend.joinToString(separator = "\n")
    }

    private fun toConfigSection(): String {
        val stringBuilder = StringBuilder()
        stringBuilder.append("listen http-in\n")
        stringBuilder.append("\tbind 0.0.0.0:80\n")
        stringBuilder.append("\tmode http\n")
        stringBuilder.append("\tbalance roundrobin\n")
        for (i in backend.indices) {
            stringBuilder.append("\tserver ${backend[i].name} ${backend[i].endpoint} weight ${backend[i].weight}\n")
        }
        return stringBuilder.toString()
    }

    fun generateConfigSections(): String {
        val stringBuilder = StringBuilder()
        stringBuilder.append(toConfigSection())
        return stringBuilder.toString()
    }
}

private fun LoadResource(resource: String): String {
    return object {}.javaClass.classLoader.getResource(resource).readText(Charsets.UTF_8)
}

fun UpdateConfig(configStr: String, ConfigFile: String):String {
    // TO-DO: sanitize input
    val config = Gson().fromJson(configStr, Config::class.java)
    File(ConfigFile).writeText(LoadResource(TEMPLATE_RESOURCE) + config.generateConfigSections())
    val reloadCommand = "docker kill -s HUP ${CONTAINER_NAME}"

    val process = Runtime.getRuntime().exec(reloadCommand)
    process.waitFor(10, TimeUnit.SECONDS)
    return when (process.isAlive) {
        true -> "HAProxy reload timed out"
        false -> when (process.exitValue()) {
            0 ->  "Success"
            else -> "HAProxy reload failed, exit code: ${process.exitValue()}"
        }
    }
}

fun main(args: Array<String>) {
    if (args.isEmpty()) {
        println("Please provide the Configuration file used by the HAProxy container as the command line argument")
        exitProcess(-1)
    } else {
        val ConfigFile = args[0]
        Spark.post("/update") { request, response ->
            var message = UpdateConfig(request.body(), ConfigFile)
            return@post "{\"message\": \"$message\"}"
        }
    }
}
