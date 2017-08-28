from OpenSSL import crypto
import argparse
from os import path
import vaultcom

#todo: clean up code, add helpful messages, error handling

parser = argparse.ArgumentParser(
    prog='PFXtoPEM',
    description='Converts MS stuff to the superior format and uploads it to Vault, if you specify the URL'
)

parser.add_argument('-password', type=str, nargs='?', default='',
                    help='The password used for the cert')

parser.add_argument('-file', type=str, nargs='?', default='', required=True,
                    help='The path to pfx file')

parser.add_argument('-url', type=str, nargs='?', default=None,
                    help='URL for vault https://x.x.x.x include the port if it is not running behind nginx')

parser.add_argument('-token', type=str, nargs='?', default='',
                    help='vault token')

parser.add_argument('-secretpath', type=str, nargs='?', default='youshouldspecifythis',
                    help='path to secret i.e /v1/secret/secretpath/secretname')

args = parser.parse_args()

pfx_password = args.password
pfx_file = args.file
vault_url = args.url
vault_token = args.token
vault_subdir = args.secretpath


class PemFormat:
    def convertpfx(self, password, file):
        # open the input file and extract data
        with open(file, 'rb') as pfx:
            pem_converter = crypto.load_pkcs12(pfx.read(), password)
            self.pem_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, pem_converter.get_privatekey())
            self.pem_cert = crypto.dump_certificate(crypto.FILETYPE_PEM, pem_converter.get_certificate())

        # write key
        pem_file = path.splitext(file)[0]
        with open(pem_file + '-key.pem', 'wb') as file:
            file.write(self.pem_key)

        # write cert
        with open(pem_file + '-cert.pem', 'wb') as file:
            file.write(self.pem_cert)

        # write ca, if any
        with open(pem_file + '-ca.pem', 'wb') as file:
            ca = pem_converter.get_ca_certificates()
            if ca is not None:
                for cert in ca:
                    self.pem_ca = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
                    file.write(self.pem_ca)

    def upload_secret(self):
        # convert the byte code to a string
        pem_key_str = self.pem_key.decode()
        pem_ca_str = self.pem_ca.decode()
        pem_cert_str = self.pem_cert.decode()

        vault_call = vaultcom.VaultCom(vault_url, vault_token, vault_subdir)
        if vault_call.get_vault_status().get('sealed') is True:
            print('Vault is sealed. Please unseal and try again')
            exit(2)
        else:
            names_dict = {'key': pem_key_str, 'ca': pem_ca_str, 'cert': pem_cert_str}
            for key, value in names_dict.items():
                upload = vault_call.put_vault_secret(key, value)
                if upload is not None:  # if it does not return 204, we know the call failed
                    print("An error occured")
                    print(upload)  # print the response
                    exit(0)

if __name__ == "__main__":
    print(f'Converting {pfx_file} to PEM')
    converter = PemFormat()
    converter.convertpfx(pfx_password, pfx_file)
    if vault_url is not None:
        converter.upload_secret()






