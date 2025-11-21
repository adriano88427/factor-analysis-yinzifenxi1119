@echo off
echo Uninstalling global Filesystem MCP...
cmd /c "npm uninstall -g @modelcontextprotocol/server-filesystem"
echo.
echo Global Filesystem MCP has been uninstalled.
echo Please configure your IDE to use the local version.
echo.
echo Configuration:
echo {
echo   "mcpServers": {
echo     "filesystem": {
echo       "command": "node",
echo       "args": ["C:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO\\mcp-filesystem\\index.js", "--allowed-directories", "C:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO"],
echo       "env": {}
echo     }
echo   }
echo }
echo.
pause