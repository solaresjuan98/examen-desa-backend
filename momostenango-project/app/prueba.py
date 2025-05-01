import requests

url = "https://siif.usac.edu.gt/WSGeneracionOrdenPago/WSGeneracionOrdenPagoSoapHttpPort"
headers = {
    "Content-Type": "text/xml; charset=utf-8",
    "SOAPAction": ""  # Puede que este campo sea requerido dependiendo del servidor
}

xml = """<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:siif="http://siif/WSAutenticacionSIIF.wsdl/types/">
    <soapenv:Header/>
    <soapenv:Body>
        <siif:validarAutenticacionElement>
            <pxml><![CDATA[
                <AUTENTICACION>
                    <TIPO_USUARIO>SISTEMA</TIPO_USUARIO>
                    <USUARIO>WSDPD</USUARIO>
                    <PASSWORD>vTfXVbt#N4UGW</PASSWORD>
                </AUTENTICACION>
            ]]></pxml>
        </siif:validarAutenticacionElement>
    </soapenv:Body>
</soapenv:Envelope>
"""

response = requests.post(url, data=xml, headers=headers)

print("Código de estado:", response.status_code)
print("Respuesta del servidor:\n", response.text)
