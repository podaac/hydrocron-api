#!/usr/bin/env python3

def main():
    from hydrocronapi import hydrocron
    hydrocron.flask_app.run(port=8080)


if __name__ == '__main__':
    main()
