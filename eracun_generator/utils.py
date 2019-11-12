import hashlib

from base64 import b64encode
from datetime import datetime, timezone

from cryptography import x509
from cryptography.hazmat.backends import default_backend

from signxml import XMLSigner

from eracun_generator.builder import build_xml


def ds_tag(tag):
    return "{http://www.w3.org/2000/09/xmldsig#}" + tag


def sign_invoice(invoice_json, key, cert):
    invoice_json = add_temp_sign_data(key, cert, invoice_json)

    xml_content = build_xml(invoice_json)

    signed_xml = XMLSigner(signature_algorithm='rsa-sha1',
                           digest_algorithm='sha1',
                           c14n_algorithm='http://www.w3.org/TR/2001/REC-xml-c14n-20010315').sign(xml_content,
                                                                                                  key=key,
                                                                                                  cert=cert,
                                                                                                  reference_uri=['data','signprops'])

    ds_object = signed_xml[1][0]

    signed_xml[1].remove(ds_object)
    signed_xml[1].append(ds_object)

    signed_xml[1].attrib['Id'] = 'signature'

    return signed_xml


def add_temp_sign_data(key, cert, invoice_json, signed_props_id='signprops'):
    pm = cert
    pem_cert = x509.load_pem_x509_certificate(pm, default_backend())

    digest = hashlib.sha1()
    digest.update(pm)
    digest = b64encode(digest.digest()).decode()

    invoice_json['signature_placeholder'] = {
        '_name': ds_tag('Signature'),
        '_attrs': [('Id', 'placeholder')]
    }

    invoice_json['signature_placeholder']['sign_temp_data'] = {
        '_name': ds_tag('Object'),
        'qualifying_props': {
            '_name': 'QualifyingProperties',
            '_attrs': [('Target', '#signature')],
            'signed_props': {
                '_name': 'SignedProperties',
                '_attrs': [('Id', signed_props_id)],
                'sign_props': {
                    '_name': 'SignedSignatureProperties',
                    'time': {
                        '_name': 'SigningTime',
                        '_value': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    },
                    'signing_cert': {
                        '_name': 'SigningCertificate',
                        'cert': {
                            '_name': 'Cert',
                            'digest': {
                                '_name': 'CertDigest',
                                'method': {
                                    '_name': 'DigestMethod',
                                    '_attrs': [('Algorithm', 'http://www.w3.org/2000/09/xmldsig#sha1')],
                                },
                                'value': {
                                    '_name': 'DigestValue',
                                    '_value': digest
                                }
                            },
                            'issuer_serial': {
                                '_name': 'IssuerSerial',
                                'name': {
                                    '_name': 'X509IssuerName',
                                   # '_attrs': [('xmlns', 'http://www.w3.org/2000/09/xmldsig#')],
                                    '_value': pem_cert.subject.rfc4514_string()
                                },
                                'serial': {
                                    '_name': 'X509SerialNumber',
                                   # '_attrs': [('xmlns', 'http://www.w3.org/2000/09/xmldsig#')],
                                    '_value': str(pem_cert.serial_number)
                                }
                            }
                        },
                    },
                    'policy': {
                        '_name': 'SignaturePolicyIdentifier',
                        'implied': {
                            '_name': 'SignaturePolicyImplied'
                        }
                    }
                }
            }
        }
    }

    return invoice_json
