# Vault-PEMfx
This converts pfx certificates to PEM and uploads them to Vault.
I wrote this while I was setting up Vault in production. I had to set up an Active Directory CA for various reasons so this tool made working with pfx certs much easier


# Usage
pfxtopem.py -file "path/to/file.pfx" -password "password" -url "http(s)://x.x.x.x:port" -token "1234-1234-1234" -secretpath "subpath"

If -url is set, it will automatically upload the secrets to the path of your choice.
The secretpath is the "subdirectory" for all secrets since Vault uses a flat file style api e.g. v1/secret/secretpath/secretname
