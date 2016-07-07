# RepoHub
Automatic monitoring of local repositories (svn,git).


![Screenshot](www/imgs/repohub.png?raw=true "Dashborad screenshot")

## Features

- [x] Web interface.
- [x] Local SVN monitoring.
- [x] Local GIT monitoring.
- [x] Visual labels for Modified/Added/Updated files in repositories.
- [x] Periodic update of distant repositories.
- [x] Update/Commit from the web interface.
- [ ] Edit settings/repositories from web interface.
- [ ] Add files button.
- 
## Install

The software requires the following software and python libraries  (for Python 3):

* tornado (python 3)
* subversion (svn command line)
* git, GitPython


under ubuntu you need only install the following:
```
sudo apt-get install python3-tornado
```

To run the RepoHub server just execute the file ```./repohub``` in the root folder.

## Config

RepoHub uses local confug file located at ~/.config/repohub.

The files ```config.ini``` and ```repos.ini``` contain respectively the global parameters of the app and the repository list.
