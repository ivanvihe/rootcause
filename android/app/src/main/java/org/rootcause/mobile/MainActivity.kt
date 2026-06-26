package org.rootcause.mobile

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import android.media.AudioAttributes
import android.media.RingtoneManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings as AndroidSettings
import androidx.core.content.FileProvider
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Badge
import androidx.compose.material3.BadgedBox
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.material3.pulltorefresh.rememberPullToRefreshState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.google.firebase.messaging.FirebaseMessaging
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.await
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URI
import java.net.URL
import java.time.Instant
import java.time.temporal.ChronoUnit

private const val DEFAULT_SERVER_HOST = "rootcause.example.com"
private const val DEFAULT_SERVER_PORT = 8567

private val ColorBackground  = Color(0xFF0B0B0D)
private val ColorSurface     = Color(0xFF141416)
private val ColorLine        = Color(0xFF2A2A2F)
private val ColorAccent      = Color(0xFFD6453C)
private val ColorSuccess     = Color(0xFF46C97E)
private val ColorWarning     = Color(0xFFE0A64B)
private val ColorError       = Color(0xFFE5564A)
private val ColorTextPrimary = Color(0xFFECECEF)
private val ColorTextSecondary = Color(0xFF8A8A93)
private val ColorTextMuted   = Color(0xFF55555E)

private enum class Screen { DASHBOARD, SETTINGS }

internal data class NotificationPrefs(
    val soundEnabled: Boolean = true,
    val bypassDnd: Boolean = false,
)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val store = AppConfigStore(applicationContext)
        val notifPrefs = store.loadNotificationPrefs()
        setupNotificationChannels(applicationContext, notifPrefs.soundEnabled, notifPrefs.bypassDnd)
        setContent {
            MaterialTheme(
                colorScheme = MaterialTheme.colorScheme.copy(
                    primary = ColorAccent,
                    secondary = ColorSuccess,
                    surface = ColorSurface,
                    background = ColorBackground,
                    onBackground = ColorTextPrimary,
                    onSurface = ColorTextPrimary,
                    onSurfaceVariant = ColorTextSecondary,
                    outline = ColorLine,
                ),
            ) {
                Surface(modifier = Modifier.fillMaxSize(), color = ColorBackground) {
                    RootCauseApp(store)
                }
            }
        }
    }
}

internal fun setupNotificationChannels(context: Context, soundEnabled: Boolean, bypassDnd: Boolean) {
    val nm = context.getSystemService(NotificationManager::class.java)
    nm.deleteNotificationChannel("rootcause_alerts")
    nm.createNotificationChannel(
        NotificationChannel("rootcause_alerts", "RootCause Alerts", NotificationManager.IMPORTANCE_HIGH).apply {
            description = "Alert notifications from RootCause"
            setBypassDnd(bypassDnd && nm.isNotificationPolicyAccessGranted)
            if (soundEnabled) {
                setSound(
                    RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION),
                    AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_NOTIFICATION_EVENT)
                        .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                        .build(),
                )
            } else {
                setSound(null, null)
            }
        },
    )
}

internal data class ServerConfig(
    val host: String,
    val port: Int,
    val apiKey: String,
    val deviceId: String = "",
) {
    fun baseUrl(): String = if (port == 443) "https://$host" else "https://$host:$port"

    companion object {
        fun fromInput(serverInput: String, fallbackPort: Int, apiKey: String, deviceId: String = ""): ServerConfig {
            val trimmed = serverInput.trim().trimEnd('/')
            val normalized = if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) trimmed else "https://$trimmed"
            val uri = URI(normalized)
            val parsedHost = uri.host?.trim().orEmpty()
            val parsedPort = if (uri.port > 0) uri.port else fallbackPort
            require(parsedHost.isNotBlank()) { "Invalid server URL" }
            return ServerConfig(host = parsedHost, port = parsedPort, apiKey = apiKey.trim(), deviceId = deviceId)
        }
    }
}

private data class MobileAlert(
    val id: String,
    val name: String,
    val status: String,
    val humanState: String,
    val detail: String,
    val targets: List<String>,
    val silencedUntil: String?,
    val silencedReason: String,
    val acknowledgedAt: String?,
    val acknowledgedBy: String,
    val paused: Boolean,
    val agentUsed: String?,
    val narrativeWhatHappened: String,
    val narrativeWhatDid: String,
    val narrativeWhatToDo: String,
)

private data class BootstrapPayload(
    val serverTimestamp: String?,
    val alerts: List<MobileAlert>,
)

private data class AppVersionInfo(
    val versionName: String,
    val versionCode: Int,
    val apkAvailable: Boolean,
    val apkSize: Long,
    val apkModified: String?,
)

internal class AppConfigStore(context: Context) {
    private val prefs = context.getSharedPreferences("rootcause_mobile", Context.MODE_PRIVATE)

    fun load(): ServerConfig? {
        val host = prefs.getString("host", "").orEmpty()
        val apiKey = prefs.getString("api_key", "").orEmpty()
        if (host.isBlank() || apiKey.isBlank()) return null
        return ServerConfig(
            host = host,
            port = prefs.getInt("port", DEFAULT_SERVER_PORT),
            apiKey = apiKey,
            deviceId = prefs.getString("device_id", "").orEmpty(),
        )
    }

    fun save(config: ServerConfig) {
        prefs.edit()
            .putString("host", config.host)
            .putInt("port", config.port)
            .putString("api_key", config.apiKey)
            .putString("device_id", config.deviceId)
            .apply()
    }

    fun savePushToken(token: String) = prefs.edit().putString("push_token", token).apply()
    fun loadPushToken(): String = prefs.getString("push_token", "").orEmpty()

    fun loadNotificationPrefs(): NotificationPrefs = NotificationPrefs(
        soundEnabled = prefs.getBoolean("notif_sound", true),
        bypassDnd = prefs.getBoolean("notif_bypass_dnd", false),
    )

    fun saveNotificationPrefs(p: NotificationPrefs) {
        prefs.edit()
            .putBoolean("notif_sound", p.soundEnabled)
            .putBoolean("notif_bypass_dnd", p.bypassDnd)
            .apply()
    }

    fun clear() = prefs.edit().clear().apply()
}

private object RootCauseApi {
    private fun request(config: ServerConfig, path: String, method: String = "GET", body: JSONObject? = null): JSONObject {
        val url = URL(config.baseUrl() + path)
        val connection = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = method
            setRequestProperty("Accept", "application/json")
            setRequestProperty("Content-Type", "application/json")
            setRequestProperty("X-API-Key", config.apiKey)
            if (config.deviceId.isNotBlank()) setRequestProperty("X-Device-Id", config.deviceId)
            connectTimeout = 10_000
            readTimeout = 15_000
            doInput = true
            if (body != null) {
                doOutput = true
                OutputStreamWriter(outputStream).use { it.write(body.toString()) }
            }
        }
        val stream = if (connection.responseCode in 200..299) connection.inputStream else connection.errorStream
        val payload = BufferedReader(InputStreamReader(stream)).use { it.readText() }
        if (connection.responseCode !in 200..299) {
            throw IllegalStateException(JSONObject(payload).optString("error", "HTTP ${connection.responseCode}"))
        }
        return JSONObject(payload)
    }

    fun register(config: ServerConfig, pushToken: String = ""): ServerConfig {
        val payload = JSONObject()
            .put("name", Build.MODEL ?: "Android")
            .put("platform", "android")
            .put("model", Build.MODEL ?: "unknown")
            .put("app_version", "0.2.0")
            .put("host", config.host)
            .put("port", config.port)
            .put("device_id", config.deviceId)
        if (pushToken.isNotBlank()) payload.put("push_token", pushToken)
        val response = request(config, "/api/mobile/device/register", "POST", payload)
        return config.copy(deviceId = response.getJSONObject("device").optString("id"))
    }

    fun bootstrap(config: ServerConfig): BootstrapPayload {
        val response = request(config, "/api/mobile/bootstrap")
        val server = response.optJSONObject("server") ?: JSONObject()
        val alerts = response.optJSONArray("alerts") ?: JSONArray()
        return BootstrapPayload(
            serverTimestamp = server.optString("timestamp").takeIf { it.isNotBlank() },
            alerts = buildList {
                for (i in 0 until alerts.length()) {
                    val item = alerts.getJSONObject(i)
                    val narrative = item.optJSONObject("narrative") ?: JSONObject()
                    add(MobileAlert(
                        id = item.optString("id"),
                        name = item.optString("name"),
                        status = item.optString("status"),
                        humanState = item.optString("human_state"),
                        detail = item.optString("detail"),
                        targets = buildList {
                            val t = item.optJSONArray("targets") ?: JSONArray()
                            for (j in 0 until t.length()) add(t.optString(j))
                        },
                        silencedUntil = item.optString("silenced_until").takeIf { it.isNotBlank() },
                        silencedReason = item.optString("silenced_reason"),
                        acknowledgedAt = item.optString("acknowledged_at").takeIf { it.isNotBlank() },
                        acknowledgedBy = item.optString("acknowledged_by"),
                        paused = item.optBoolean("paused"),
                        agentUsed = item.optString("agent_used").takeIf { it.isNotBlank() },
                        narrativeWhatHappened = narrative.optString("what_happened"),
                        narrativeWhatDid = narrative.optString("what_rootcause_did"),
                        narrativeWhatToDo = narrative.optString("what_you_should_do"),
                    ))
                }
            },
        )
    }

    fun acknowledge(config: ServerConfig, alertId: String) {
        request(config, "/api/mobile/action/ack", "POST", JSONObject().put("alert_id", alertId))
    }

    fun silence(config: ServerConfig, alertId: String, minutes: Int = 60) {
        request(config, "/api/mobile/action/silence", "POST",
            JSONObject().put("alert_id", alertId).put("minutes", minutes).put("reason", "Silenced from mobile"))
    }

    fun rerun(config: ServerConfig, alertId: String) {
        request(config, "/api/mobile/action/rerun", "POST", JSONObject().put("alert_id", alertId))
    }

    fun checkAppVersion(config: ServerConfig): AppVersionInfo {
        val resp = request(config, "/api/mobile/app-version")
        return AppVersionInfo(
            versionName = resp.optString("version_name", "unknown"),
            versionCode = resp.optInt("version_code", 0),
            apkAvailable = resp.optBoolean("apk_available", false),
            apkSize = resp.optLong("apk_size", 0L),
            apkModified = resp.optString("apk_modified").takeIf { it.isNotBlank() },
        )
    }

    fun downloadApk(config: ServerConfig, destFile: File, onProgress: (Int) -> Unit) {
        val url = java.net.URL(config.baseUrl() + "/api/mobile/download-apk")
        val conn = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "GET"
            setRequestProperty("X-API-Key", config.apiKey)
            if (config.deviceId.isNotBlank()) setRequestProperty("X-Device-Id", config.deviceId)
            connectTimeout = 10_000
            readTimeout = 60_000
        }
        if (conn.responseCode !in 200..299) {
            throw IllegalStateException("Download failed: HTTP ${conn.responseCode}")
        }
        val total = conn.contentLengthLong
        conn.inputStream.use { input ->
            FileOutputStream(destFile).use { output ->
                val buf = ByteArray(8192)
                var downloaded = 0L
                var read: Int
                while (input.read(buf).also { read = it } != -1) {
                    output.write(buf, 0, read)
                    downloaded += read
                    if (total > 0) onProgress(((downloaded * 100) / total).toInt())
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun RootCauseApp(store: AppConfigStore) {
    val context = LocalContext.current
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()
    val initial = remember { store.load() }
    var serverConfig by remember { mutableStateOf(initial) }
    var lastConfig by remember { mutableStateOf(initial) }
    var bootstrap by remember { mutableStateOf<BootstrapPayload?>(null) }
    var loading by remember { mutableStateOf(false) }
    var screen by remember { mutableStateOf(Screen.DASHBOARD) }
    var notifPrefs by remember { mutableStateOf(store.loadNotificationPrefs()) }
    val jobHolder = remember { object { var job: Job? = null } }

    LaunchedEffect(notifPrefs.soundEnabled, notifPrefs.bypassDnd) {
        setupNotificationChannels(context, notifPrefs.soundEnabled, notifPrefs.bypassDnd)
    }

    fun refresh(config: ServerConfig) {
        jobHolder.job?.cancel()
        jobHolder.job = scope.launch {
            loading = true
            try {
                val pushToken = runCatching { FirebaseMessaging.getInstance().token.await() }.getOrElse { store.loadPushToken() }
                if (pushToken.isNotBlank()) store.savePushToken(pushToken)
                val registered = withContext(Dispatchers.IO) { RootCauseApi.register(config, pushToken) }
                store.save(registered)
                serverConfig = registered
                lastConfig = registered
                bootstrap = withContext(Dispatchers.IO) { RootCauseApi.bootstrap(registered) }
            } catch (error: Exception) {
                if (error is CancellationException) throw error
                snackbarHostState.showSnackbar(error.message ?: "Connection failed")
            } finally {
                loading = false
            }
        }
    }

    fun disconnect() {
        jobHolder.job?.cancel()
        jobHolder.job = null
        store.clear()
        serverConfig = null
        bootstrap = null
        loading = false
        screen = Screen.DASHBOARD
    }

    val failingCount = bootstrap?.alerts?.count { it.status == "failing" || it.status == "idle" } ?: 0

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = ColorBackground,
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        if (screen == Screen.SETTINGS) {
                            IconButton(onClick = { screen = Screen.DASHBOARD }) {
                                Text("←", color = ColorTextPrimary, fontSize = 20.sp)
                            }
                        }
                        Icon(
                            painter = painterResource(R.drawable.rootcause_logo),
                            contentDescription = null,
                            tint = Color.Unspecified,
                            modifier = Modifier.size(28.dp),
                        )
                        Text("rootcause", color = ColorTextPrimary, fontWeight = FontWeight.Bold)
                        if (screen == Screen.SETTINGS) {
                            Text("/ Settings", color = ColorTextMuted, fontWeight = FontWeight.Normal)
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = ColorBackground),
                actions = {
                    if (serverConfig != null && screen == Screen.DASHBOARD) {
                        if (loading) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(20.dp).padding(end = 4.dp),
                                strokeWidth = 2.dp,
                                color = ColorAccent,
                            )
                        } else {
                            BadgedBox(
                                badge = {
                                    if (failingCount > 0) {
                                        Badge(containerColor = ColorError) {
                                            Text(failingCount.toString(), fontSize = 10.sp)
                                        }
                                    }
                                },
                            ) {
                                IconButton(onClick = { refresh(serverConfig!!) }) {
                                    Text("↻", color = ColorTextPrimary, fontSize = 18.sp)
                                }
                            }
                        }
                        IconButton(onClick = { screen = Screen.SETTINGS }) {
                            Text("⚙", color = ColorTextSecondary, fontSize = 16.sp)
                        }
                    }
                },
            )
        },
    ) { padding ->
        when {
            serverConfig == null -> OnboardingScreen(
                modifier = Modifier.padding(padding),
                initialUrl = lastConfig?.baseUrl() ?: "https://$DEFAULT_SERVER_HOST:$DEFAULT_SERVER_PORT",
                initialPort = lastConfig?.port?.toString() ?: DEFAULT_SERVER_PORT.toString(),
                initialApiKey = lastConfig?.apiKey ?: "",
                onConnect = { config ->
                    store.save(config)
                    lastConfig = config
                    serverConfig = config
                    refresh(config)
                },
            )
            screen == Screen.SETTINGS -> SettingsScreen(
                modifier = Modifier.padding(padding),
                config = serverConfig!!,
                store = store,
                notifPrefs = notifPrefs,
                onNotifPrefsChange = { prefs ->
                    notifPrefs = prefs
                    store.saveNotificationPrefs(prefs)
                },
                onSaveConnection = { updated ->
                    store.save(updated)
                    lastConfig = updated
                    serverConfig = updated
                    refresh(updated)
                },
                onDisconnect = { disconnect() },
            )
            else -> {
                if (bootstrap == null && !loading) refresh(serverConfig!!)
                DashboardScreen(
                    modifier = Modifier.padding(padding),
                    payload = bootstrap,
                    loading = loading,
                    onRefresh = { refresh(serverConfig!!) },
                    onAck = { alertId ->
                        scope.launch {
                            try {
                                withContext(Dispatchers.IO) { RootCauseApi.acknowledge(serverConfig!!, alertId) }
                                refresh(serverConfig!!)
                            } catch (e: Exception) { snackbarHostState.showSnackbar(e.message ?: "Action failed") }
                        }
                    },
                    onSilence = { alertId ->
                        scope.launch {
                            try {
                                withContext(Dispatchers.IO) { RootCauseApi.silence(serverConfig!!, alertId) }
                                refresh(serverConfig!!)
                            } catch (e: Exception) { snackbarHostState.showSnackbar(e.message ?: "Action failed") }
                        }
                    },
                    onRerun = { alertId ->
                        scope.launch {
                            try {
                                withContext(Dispatchers.IO) { RootCauseApi.rerun(serverConfig!!, alertId) }
                                refresh(serverConfig!!)
                            } catch (e: Exception) { snackbarHostState.showSnackbar(e.message ?: "Action failed") }
                        }
                    },
                )
            }
        }
    }
}

@Composable
private fun OnboardingScreen(
    modifier: Modifier = Modifier,
    initialUrl: String,
    initialPort: String,
    initialApiKey: String,
    onConnect: (ServerConfig) -> Unit,
) {
    var serverInput by rememberSaveable { mutableStateOf(initialUrl) }
    var port by rememberSaveable { mutableStateOf(initialPort) }
    var apiKey by rememberSaveable { mutableStateOf(initialApiKey) }
    var validationError by rememberSaveable { mutableStateOf<String?>(null) }

    Column(
        modifier = modifier
            .fillMaxWidth()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 24.dp)
            .padding(top = 48.dp, bottom = 24.dp),
    ) {
        Text("RootCause", style = MaterialTheme.typography.headlineLarge, color = ColorTextPrimary, fontWeight = FontWeight.Bold)
        Text("Connect to your server", style = MaterialTheme.typography.bodyLarge, color = ColorTextSecondary)
        Spacer(Modifier.height(32.dp))
        OutlinedTextField(
            value = serverInput,
            onValueChange = { serverInput = it; validationError = null },
            label = { Text("Server URL") },
            placeholder = { Text("https://rootcause.example.com:8443") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
        )
        Spacer(Modifier.height(12.dp))
        OutlinedTextField(
            value = port,
            onValueChange = { port = it; validationError = null },
            label = { Text("Fallback port") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
        )
        Spacer(Modifier.height(12.dp))
        OutlinedTextField(
            value = apiKey,
            onValueChange = { apiKey = it; validationError = null },
            label = { Text("API key") },
            placeholder = { Text("ank_live_...") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
        )
        Spacer(Modifier.height(8.dp))
        Text("Paste the full URL — host and port are extracted automatically.", color = ColorTextMuted, style = MaterialTheme.typography.bodySmall)
        if (validationError != null) {
            Spacer(Modifier.height(8.dp))
            Text(validationError!!, color = ColorError, style = MaterialTheme.typography.bodySmall)
        }
        Spacer(Modifier.height(24.dp))
        Button(
            onClick = {
                runCatching {
                    ServerConfig.fromInput(serverInput, port.toIntOrNull() ?: DEFAULT_SERVER_PORT, apiKey)
                }.onSuccess(onConnect).onFailure { validationError = it.message ?: "Invalid configuration" }
            },
            modifier = Modifier.fillMaxWidth(),
        ) { Text("Connect", fontWeight = FontWeight.SemiBold) }
    }
}

@Composable
private fun SettingsScreen(
    modifier: Modifier = Modifier,
    config: ServerConfig,
    store: AppConfigStore,
    notifPrefs: NotificationPrefs,
    onNotifPrefsChange: (NotificationPrefs) -> Unit,
    onSaveConnection: (ServerConfig) -> Unit,
    onDisconnect: () -> Unit,
) {
    val context = LocalContext.current
    val nm = remember { context.getSystemService(NotificationManager::class.java) }
    val pushToken = remember { store.loadPushToken() }
    var serverInput by rememberSaveable(config.host, config.port) { mutableStateOf(config.baseUrl()) }
    var portInput by rememberSaveable(config.port) { mutableStateOf(config.port.toString()) }
    var apiKeyInput by rememberSaveable(config.apiKey) { mutableStateOf(config.apiKey) }
    var connectionStatus by rememberSaveable { mutableStateOf<String?>(null) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // Connection section
        SettingsCard(title = "Connection") {
            OutlinedTextField(
                value = serverInput,
                onValueChange = {
                    serverInput = it
                    connectionStatus = null
                },
                label = { Text("Server URL") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )
            Spacer(Modifier.height(10.dp))
            OutlinedTextField(
                value = portInput,
                onValueChange = {
                    portInput = it
                    connectionStatus = null
                },
                label = { Text("Fallback port") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )
            Spacer(Modifier.height(10.dp))
            OutlinedTextField(
                value = apiKeyInput,
                onValueChange = {
                    apiKeyInput = it
                    connectionStatus = null
                },
                label = { Text("API key") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )
            Spacer(Modifier.height(8.dp))
            Text("Change host, port or API key here and the app will reconnect with the new settings.", color = ColorTextMuted, style = MaterialTheme.typography.bodySmall)
            if (connectionStatus != null) {
                Spacer(Modifier.height(8.dp))
                Text(
                    connectionStatus!!,
                    color = if (connectionStatus!!.startsWith("Saved")) ColorSuccess else ColorError,
                    style = MaterialTheme.typography.bodySmall,
                )
            }
            Spacer(Modifier.height(12.dp))
            Button(
                onClick = {
                    runCatching {
                        ServerConfig.fromInput(
                            serverInput,
                            portInput.toIntOrNull() ?: DEFAULT_SERVER_PORT,
                            apiKeyInput,
                            config.deviceId,
                        )
                    }.onSuccess {
                        connectionStatus = "Saved. Reconnecting..."
                        onSaveConnection(it)
                    }.onFailure {
                        connectionStatus = it.message ?: "Invalid configuration"
                    }
                },
                modifier = Modifier.fillMaxWidth(),
            ) { Text("Save and reconnect", fontWeight = FontWeight.SemiBold) }
            Spacer(Modifier.height(12.dp))
            HorizontalDivider(color = ColorSurface)
            SettingsInfoRow("Current device ID", config.deviceId.ifBlank { "not registered" })
            Spacer(Modifier.height(12.dp))
            TextButton(
                onClick = onDisconnect,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("Disconnect and reconfigure", color = ColorError) }
        }

        // Notifications section
        SettingsCard(title = "Notifications") {
            SettingsToggleRow(
                label = "Sound",
                description = "Play sound on new alerts",
                checked = notifPrefs.soundEnabled,
                onCheckedChange = { onNotifPrefsChange(notifPrefs.copy(soundEnabled = it)) },
            )
            HorizontalDivider(color = ColorSurface)
            val dndGranted = nm.isNotificationPolicyAccessGranted
            SettingsToggleRow(
                label = "Override Do Not Disturb",
                description = when {
                    dndGranted && notifPrefs.bypassDnd -> "Active — alerts ring even when phone is silenced"
                    dndGranted -> "Permission granted — toggle to enable"
                    else -> "Permission required — toggle to open system settings"
                },
                checked = notifPrefs.bypassDnd && dndGranted,
                onCheckedChange = { enable: Boolean ->
                    if (enable && !dndGranted) {
                        context.startActivity(Intent(AndroidSettings.ACTION_NOTIFICATION_POLICY_ACCESS_SETTINGS))
                    } else {
                        onNotifPrefsChange(notifPrefs.copy(bypassDnd = enable))
                    }
                },
            )
        }

        // Push notifications section
        SettingsCard(title = "Push Notifications") {
            if (pushToken.isBlank()) {
                SettingsInfoRow("Status", "No push token — open app to register")
            } else {
                SettingsInfoRow("Status", "Active")
                HorizontalDivider(color = ColorSurface)
                SettingsInfoRow("Token", "${pushToken.take(20)}…")
            }
        }

        // Update section
        AppUpdateCard(config = config, scope = rememberCoroutineScope())

        // About section
        SettingsCard(title = "About") {
            SettingsInfoRow("App version", "${BuildConfig.VERSION_NAME} (${BuildConfig.VERSION_CODE})")
            HorizontalDivider(color = ColorLine)
            SettingsInfoRow("Platform", "Android ${Build.VERSION.RELEASE}")
        }
    }
}

private sealed interface UpdateState {
    data object Idle : UpdateState
    data object Checking : UpdateState
    data object UpToDate : UpdateState
    data class UpdateAvailable(val info: AppVersionInfo) : UpdateState
    data class Downloading(val progress: Int) : UpdateState
    data class Error(val message: String) : UpdateState
}

@Composable
private fun AppUpdateCard(config: ServerConfig, scope: kotlinx.coroutines.CoroutineScope) {
    val context = LocalContext.current
    var state by remember { mutableStateOf<UpdateState>(UpdateState.Idle) }

    fun installApk(apkFile: File) {
        val uri = FileProvider.getUriForFile(context, "${context.packageName}.fileprovider", apkFile)
        val intent = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "application/vnd.android.package-archive")
            flags = Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK
        }
        context.startActivity(intent)
    }

    fun checkForUpdate() {
        state = UpdateState.Checking
        scope.launch {
            try {
                val info = withContext(Dispatchers.IO) { RootCauseApi.checkAppVersion(config) }
                state = if (!info.apkAvailable) {
                    UpdateState.Error("No APK available on server")
                } else if (info.versionCode > BuildConfig.VERSION_CODE) {
                    UpdateState.UpdateAvailable(info)
                } else {
                    UpdateState.UpToDate
                }
            } catch (e: Exception) {
                if (e is CancellationException) throw e
                state = UpdateState.Error(e.message ?: "Check failed")
            }
        }
    }

    fun downloadAndInstall(info: AppVersionInfo) {
        state = UpdateState.Downloading(0)
        scope.launch {
            try {
                val destFile = File(context.cacheDir, "rootcause_update.apk")
                withContext(Dispatchers.IO) {
                    RootCauseApi.downloadApk(config, destFile) { progress ->
                        state = UpdateState.Downloading(progress)
                    }
                }
                installApk(destFile)
                state = UpdateState.Idle
            } catch (e: Exception) {
                if (e is CancellationException) throw e
                state = UpdateState.Error(e.message ?: "Download failed")
            }
        }
    }

    SettingsCard(title = "App Update") {
        when (val s = state) {
            is UpdateState.Idle -> {
                SettingsInfoRow("Installed", "${BuildConfig.VERSION_NAME} (${BuildConfig.VERSION_CODE})")
                Spacer(Modifier.height(8.dp))
                Button(onClick = { checkForUpdate() }, modifier = Modifier.fillMaxWidth()) {
                    Text("Check for update", fontWeight = FontWeight.SemiBold)
                }
            }
            is UpdateState.Checking -> {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    CircularProgressIndicator(modifier = Modifier.size(18.dp), strokeWidth = 2.dp, color = ColorAccent)
                    Text("Checking server…", color = ColorTextSecondary, style = MaterialTheme.typography.bodyMedium)
                }
            }
            is UpdateState.UpToDate -> {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("✓", color = ColorSuccess, fontSize = 18.sp)
                    Text("Up to date — ${BuildConfig.VERSION_NAME}", color = ColorSuccess, style = MaterialTheme.typography.bodyMedium)
                }
                Spacer(Modifier.height(8.dp))
                TextButton(onClick = { state = UpdateState.Idle }, modifier = Modifier.fillMaxWidth()) {
                    Text("Check again", color = ColorTextMuted, style = MaterialTheme.typography.labelMedium)
                }
            }
            is UpdateState.UpdateAvailable -> {
                val sizeMb = "%.1f MB".format(s.info.apkSize / 1_048_576f)
                SettingsInfoRow("Installed", "${BuildConfig.VERSION_NAME} (${BuildConfig.VERSION_CODE})")
                HorizontalDivider(color = ColorLine)
                SettingsInfoRow("Available", "${s.info.versionName} (${s.info.versionCode})")
                Spacer(Modifier.height(4.dp))
                Text("$sizeMb · tap to download and install", color = ColorTextMuted, style = MaterialTheme.typography.bodySmall)
                Spacer(Modifier.height(10.dp))
                Button(
                    onClick = { downloadAndInstall(s.info) },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = ColorAccent),
                ) {
                    Text("Download & Install", fontWeight = FontWeight.SemiBold)
                }
            }
            is UpdateState.Downloading -> {
                Text("Downloading update…", color = ColorTextSecondary, style = MaterialTheme.typography.bodyMedium)
                Spacer(Modifier.height(8.dp))
                LinearProgressIndicator(
                    progress = { s.progress / 100f },
                    modifier = Modifier.fillMaxWidth(),
                    color = ColorAccent,
                    trackColor = ColorLine,
                )
                Spacer(Modifier.height(4.dp))
                Text("${s.progress}%", color = ColorTextMuted, style = MaterialTheme.typography.labelSmall)
            }
            is UpdateState.Error -> {
                Text(s.message, color = ColorError, style = MaterialTheme.typography.bodySmall)
                Spacer(Modifier.height(8.dp))
                TextButton(onClick = { state = UpdateState.Idle }, modifier = Modifier.fillMaxWidth()) {
                    Text("Retry", color = ColorAccent, style = MaterialTheme.typography.labelMedium)
                }
            }
        }
    }
}

@Composable
private fun SettingsCard(title: String, content: @Composable ColumnScope.() -> Unit) {
    Card(
        colors = CardDefaults.cardColors(containerColor = ColorSurface),
        elevation = CardDefaults.cardElevation(0.dp),
        border = BorderStroke(1.dp, ColorLine),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(Modifier.padding(16.dp)) {
            Text(title, color = ColorTextMuted, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(12.dp))
            content()
        }
    }
}

@Composable
private fun SettingsInfoRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(label, color = ColorTextSecondary, style = MaterialTheme.typography.bodyMedium)
        Text(value, color = ColorTextPrimary, style = MaterialTheme.typography.bodyMedium, maxLines = 1, overflow = TextOverflow.Ellipsis, modifier = Modifier.padding(start = 16.dp))
    }
}

@Composable
private fun SettingsToggleRow(label: String, description: String, checked: Boolean, onCheckedChange: (Boolean) -> Unit) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(Modifier.weight(1f).padding(end = 12.dp)) {
            Text(label, color = ColorTextPrimary, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Medium)
            Text(description, color = ColorTextMuted, style = MaterialTheme.typography.bodySmall)
        }
        Switch(
            checked = checked,
            onCheckedChange = onCheckedChange,
            colors = SwitchDefaults.colors(
                checkedThumbColor = ColorAccent,
                checkedTrackColor = ColorAccent.copy(alpha = 0.3f),
            ),
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun DashboardScreen(
    modifier: Modifier = Modifier,
    payload: BootstrapPayload?,
    loading: Boolean,
    onRefresh: () -> Unit,
    onAck: (String) -> Unit,
    onSilence: (String) -> Unit,
    onRerun: (String) -> Unit,
) {
    val pullState = rememberPullToRefreshState()

    PullToRefreshBox(isRefreshing = loading, onRefresh = onRefresh, state = pullState, modifier = modifier.fillMaxSize()) {
        if (payload == null && loading) {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    CircularProgressIndicator(color = ColorAccent)
                    Spacer(Modifier.height(16.dp))
                    Text("Connecting…", color = ColorTextSecondary)
                }
            }
        } else {
            val failing = payload?.alerts?.filter { it.status == "failing" } ?: emptyList()
            val idle = payload?.alerts?.filter { it.status == "idle" } ?: emptyList()
            val ok = payload?.alerts?.filter { it.status != "failing" && it.status != "idle" } ?: emptyList()

            LazyColumn(
                modifier = Modifier.fillMaxSize().background(ColorBackground).padding(horizontal = 14.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp),
                contentPadding = androidx.compose.foundation.layout.PaddingValues(vertical = 14.dp),
            ) {
                item { SummaryCard(payload, failing.size, idle.size, ok.size) }

                if (failing.isEmpty() && idle.isEmpty() && payload != null) {
                    item { AllGoodCard() }
                }
                if (failing.isNotEmpty()) {
                    item { SectionHeader("Failing", failing.size, ColorError) }
                    items(failing) { AlertCard(it, onAck, onSilence, onRerun) }
                }
                if (idle.isNotEmpty()) {
                    item { SectionHeader("Idle / Paused", idle.size, ColorWarning) }
                    items(idle) { AlertCard(it, onAck, onSilence, onRerun) }
                }
                if (ok.isNotEmpty()) {
                    item { SectionHeader("OK", ok.size, ColorSuccess) }
                    items(ok) { AlertCard(it, onAck, onSilence, onRerun, compact = true) }
                }
            }
        }
    }
}

@Composable
private fun SummaryCard(payload: BootstrapPayload?, failing: Int, idle: Int, ok: Int) {
    Card(
        colors = CardDefaults.cardColors(containerColor = ColorSurface),
        elevation = CardDefaults.cardElevation(0.dp),
        border = BorderStroke(1.dp, ColorLine),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text("Status", color = ColorTextPrimary, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                if (payload?.serverTimestamp != null) {
                    Text(formatTimestampRelative(payload.serverTimestamp), color = ColorTextMuted, style = MaterialTheme.typography.labelSmall)
                }
            }
            Spacer(Modifier.height(12.dp))
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                StatPill("Failing", failing, ColorError, Modifier.weight(1f))
                StatPill("Idle", idle, ColorWarning, Modifier.weight(1f))
                StatPill("OK", ok, ColorSuccess, Modifier.weight(1f))
            }
        }
    }
}

@Composable
private fun StatPill(label: String, count: Int, color: Color, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier.background(color.copy(alpha = 0.12f), RoundedCornerShape(8.dp)).padding(vertical = 10.dp, horizontal = 8.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(count.toString(), color = color, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
        Text(label, color = color.copy(alpha = 0.8f), style = MaterialTheme.typography.labelSmall)
    }
}

@Composable
private fun AllGoodCard() {
    Card(
        colors = CardDefaults.cardColors(containerColor = ColorSurface),
        elevation = CardDefaults.cardElevation(0.dp),
        border = BorderStroke(1.dp, ColorSuccess.copy(alpha = 0.25f)),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Row(Modifier.padding(20.dp).fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.Center) {
            Text("✓", color = ColorSuccess, fontSize = 24.sp)
            Spacer(Modifier.width(12.dp))
            Text("All checks passing", color = ColorSuccess, fontWeight = FontWeight.SemiBold)
        }
    }
}

@Composable
private fun SectionHeader(title: String, count: Int, color: Color) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 2.dp, vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Box(Modifier.size(8.dp).background(color, RoundedCornerShape(4.dp)))
        Text(title, color = color, fontWeight = FontWeight.SemiBold, style = MaterialTheme.typography.labelLarge)
        Text("($count)", color = color.copy(alpha = 0.6f), style = MaterialTheme.typography.labelMedium)
    }
}

@Composable
private fun AlertCard(
    alert: MobileAlert,
    onAck: (String) -> Unit,
    onSilence: (String) -> Unit,
    onRerun: (String) -> Unit,
    compact: Boolean = false,
) {
    val needsYou = alert.humanState == "needs_you" || (alert.status == "idle" && alert.humanState.isBlank())
    val statusColor = when {
        needsYou -> ColorError
        alert.status == "failing" -> ColorWarning
        else -> ColorSuccess
    }
    val borderColor = statusColor.copy(alpha = if (needsYou || alert.status == "failing") 0.45f else 0.18f)
    val isAcknowledged = alert.acknowledgedAt != null
    val isSilenced = alert.silencedUntil != null
    val cardAlpha = if (isAcknowledged || isSilenced) 0.7f else 1f

    Card(
        colors = CardDefaults.cardColors(containerColor = ColorSurface),
        elevation = CardDefaults.cardElevation(0.dp),
        border = BorderStroke(1.dp, borderColor),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Row(Modifier.fillMaxWidth()) {
            Box(
                Modifier
                    .width(4.dp)
                    .height(if (compact) 52.dp else 120.dp)
                    .background(statusColor.copy(alpha = cardAlpha), RoundedCornerShape(topStart = 12.dp, bottomStart = 12.dp)),
            )
            Column(
                Modifier.padding(start = 12.dp, top = 12.dp, end = 12.dp, bottom = if (compact) 12.dp else 8.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        alert.name,
                        color = ColorTextPrimary.copy(alpha = cardAlpha),
                        fontWeight = FontWeight.SemiBold,
                        style = MaterialTheme.typography.bodyLarge,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                        modifier = Modifier.weight(1f),
                    )
                    Spacer(Modifier.width(8.dp))
                    StatusBadge(alert)
                }
                if (!compact) {
                    val whatHappened = alert.narrativeWhatHappened.ifBlank { alert.detail }
                    val whatToDo = alert.narrativeWhatToDo
                    val whatDid = alert.narrativeWhatDid
                    if (whatHappened.isNotBlank()) {
                        Spacer(Modifier.height(2.dp))
                        NarrativeRow("QUÉ PASA", whatHappened, ColorTextSecondary)
                    }
                    if (whatDid.isNotBlank()) {
                        NarrativeRow("RootCause", whatDid, ColorTextMuted)
                    }
                    if (whatToDo.isNotBlank() && needsYou) {
                        NarrativeRow("QUÉ HACER", whatToDo, ColorError)
                    }
                    if (alert.targets.isNotEmpty()) {
                        Spacer(Modifier.height(2.dp))
                        Text(alert.targets.joinToString(" · "), color = ColorTextMuted, style = MaterialTheme.typography.labelSmall, maxLines = 1, overflow = TextOverflow.Ellipsis)
                    }
                    if (isAcknowledged) {
                        val by = if (alert.acknowledgedBy.isNotBlank()) " by ${alert.acknowledgedBy}" else ""
                        Text("Acknowledged$by", color = ColorSuccess.copy(alpha = 0.8f), style = MaterialTheme.typography.labelSmall)
                    }
                    if (isSilenced) {
                        val remaining = formatSilenceRemaining(alert.silencedUntil!!)
                        val reason = if (alert.silencedReason.isNotBlank()) " · ${alert.silencedReason}" else ""
                        Text("Silenced $remaining$reason", color = ColorWarning.copy(alpha = 0.8f), style = MaterialTheme.typography.labelSmall)
                    }
                    if (alert.agentUsed != null) {
                        Text("via ${alert.agentUsed}", color = ColorTextMuted, style = MaterialTheme.typography.labelSmall)
                    }
                    Row(horizontalArrangement = Arrangement.spacedBy(0.dp)) {
                        TextButton(onClick = { onAck(alert.id) }, contentPadding = androidx.compose.foundation.layout.PaddingValues(horizontal = 8.dp, vertical = 4.dp)) {
                            Text("Ack", color = ColorAccent, style = MaterialTheme.typography.labelMedium)
                        }
                        TextButton(onClick = { onSilence(alert.id) }, contentPadding = androidx.compose.foundation.layout.PaddingValues(horizontal = 8.dp, vertical = 4.dp)) {
                            Text("Silence 1h", color = ColorWarning, style = MaterialTheme.typography.labelMedium)
                        }
                        TextButton(onClick = { onRerun(alert.id) }, contentPadding = androidx.compose.foundation.layout.PaddingValues(horizontal = 8.dp, vertical = 4.dp)) {
                            Text("Re-run", color = ColorTextSecondary, style = MaterialTheme.typography.labelMedium)
                        }
                    }
                } else {
                    if (alert.targets.isNotEmpty()) {
                        Text(alert.targets.joinToString(" · "), color = ColorTextMuted, style = MaterialTheme.typography.labelSmall)
                    }
                }
            }
        }
    }
}

@Composable
private fun NarrativeRow(label: String, text: String, textColor: Color) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 1.dp),
        horizontalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Text(
            label,
            color = ColorTextMuted,
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.width(60.dp).padding(top = 1.dp),
        )
        Text(
            text,
            color = textColor,
            style = MaterialTheme.typography.bodySmall,
            maxLines = 2,
            overflow = TextOverflow.Ellipsis,
            modifier = Modifier.weight(1f),
        )
    }
}

@Composable
private fun StatusBadge(alert: MobileAlert) {
    val (label, color) = when {
        alert.acknowledgedAt != null -> "ACK'D" to ColorSuccess
        alert.silencedUntil != null -> "MUTED" to ColorWarning
        alert.humanState == "needs_you" || alert.status == "idle" -> "NEEDS YOU" to ColorError
        alert.humanState == "acting" || alert.status == "failing" -> "ACTING" to ColorWarning
        alert.humanState == "resolved_auto" -> "RESOLVED" to ColorSuccess
        else -> "OK" to ColorSuccess
    }
    Box(
        modifier = Modifier.background(color.copy(alpha = 0.18f), RoundedCornerShape(4.dp)).padding(horizontal = 6.dp, vertical = 3.dp),
    ) {
        Text(label, color = color, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.labelSmall)
    }
}

private fun formatTimestampRelative(iso: String): String {
    return try {
        val seconds = ChronoUnit.SECONDS.between(Instant.parse(iso), Instant.now())
        when {
            seconds < 60 -> "just now"
            seconds < 3600 -> "${seconds / 60}m ago"
            else -> "${seconds / 3600}h ago"
        }
    } catch (_: Exception) { "" }
}

private fun formatSilenceRemaining(iso: String): String {
    return try {
        val seconds = ChronoUnit.SECONDS.between(Instant.now(), Instant.parse(iso))
        when {
            seconds <= 0 -> "(expired)"
            seconds < 3600 -> "for ${seconds / 60}m"
            else -> "for ${seconds / 3600}h ${(seconds % 3600) / 60}m"
        }
    } catch (_: Exception) { "" }
}
