# dlhd-proxy 🚀

A lightweight, headless IPTV proxy that fetches channel metadata, exposes a playlist at `/playlist.m3u8`, serves an XMLTV guide at `/guide.xml`, and proxies stream requests for every channel.

**11/25/26 - Upstream domain changed to `dlhd.dad` and now requires Flaresolverr for page loads. However, dealing with issue where DLHD has blocked direct access to their streams as well, so currently NOT WORKING.**

---

## ✨ Features

- **📄 Playlist & Guide**: Fetch channels, expose `playlist.m3u8`, and serve `guide.xml`.
- **🔗 Stream Proxying**: `/stream/{channel_id}.m3u8` rewrites upstream playlists and proxies segment/key requests.
- **✅ Channel Filtering**: Control which channels appear in the playlist/guide through a config file.
- **🕒 Daily Guide Updates**: Automatically refresh `guide.xml` once per day at a user-defined time.
- **⚙️ Docker-First Hosting**: Run the application using Docker or Docker Compose with flexible configuration options.

---

## 🐳 Docker Installation (Headless)

> ⚠️ **Important:** When exposing the application on your local network (LAN), set `API_URL` in your `.env` file to the **local IP address** of the server hosting the container so that playlist entries resolve correctly.

1. Install Docker and Docker Compose.
2. Clone the repository and change into the project directory.
3. Copy the example configuration files and adjust them for your environment:
   ```bash
   cp .env.example .env
   cp docker-compose.yml.example docker-compose.yml
   ```
4. Start the application with Docker Compose:
   ```bash
   docker compose up -d
   ```

To run with plain Docker:

```bash
docker build -t dlhd-proxy .
docker run -p 3000:3000 dlhd-proxy
```

---

## ⚙️ Configuration

### Environment Variables

- **PORT**: Set a custom port for the server.
- **API_URL**: Set the domain or IP (including scheme) where the server is reachable; used to build stream URLs inside the playlist.
- **SOCKS5**: Proxy DLHD traffic through a SOCKS5 server if needed.
- **FLARESOLVERR_URL** *(recommended)*: Endpoint for your Flaresolverr instance (e.g., `http://localhost:8191/v1`). Requests to `dlhd.dad` are routed through Flaresolverr when this is set.
- **FLARESOLVERR_TIMEOUT**: Timeout (in seconds) for Flaresolverr requests (default: `60`).
- **PROXY_CONTENT**: Proxy video content itself through your server (optional).
- **TZ**: Timezone used for schedules and guide generation (e.g., `America/New_York`).
- **GUIDE_UPDATE**: Daily time (`HH:MM`) to refresh `guide.xml`.
- **DLHD_PROXY_KEY_FILE** *(optional)*: Override the location of the persisted token encryption key (defaults to `data/token.key`).

Copy `.env.example` to `.env` (as shown above) and edit the local `.env` to customise your environment variables.

### Playlist Channel Selection

Channel allowlisting is controlled by `data/playlist.json` (override with `PLAYLIST_CONFIG`). Populate it with the channel IDs you want included in the playlist and guide:

```json
{
  "playlist_channels": ["101", "202", "303"]
}
```

If the file is absent, every discovered channel is included by default. Legacy files (`data/selected_channels.json` or `channels.json`) are still read and migrated automatically.

An example file is provided at `playlist.example.json`.

### Example Docker Command
```bash
docker build -t dlhd-proxy .
docker run -e PROXY_CONTENT=FALSE -e API_URL=https://example.com -e SOCKS5=user:password@proxy.example.com:1080 -p 3000:3000 dlhd-proxy
```
