# pylint: disable=C0116
# pylint: disable=C0114
# pylint: disable=E0401

import connexion


def main():
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.add_api('swagger.yaml',
                arguments={'title': 'Get time series data from SWOT observations for reaches, nodes, and/or lakes'},
                pythonic_params=True)
    app.run(port=8081)


if __name__ == '__main__':
    main()
