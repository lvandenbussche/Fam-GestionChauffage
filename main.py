from main.ota_updater import OTAUpdater


def download_and_install_update_if_available():
    o = OTAUpdater('https://github.com/lvandenbussche/Fam-GestionChauffage.git')
    o.download_and_install_update_if_available('101', 'wifigest')


def start():
    pass


def boot():
    download_and_install_update_if_available()
    start()


boot()
