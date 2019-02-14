# templatizator
===============

[![BSD license][license]](https://raw.githubusercontent.com/jhonasn/templatizator/master/LICENSE)
[![Build Status](https://travis-ci.org/jhonasn/templatizator.svg?branch=master)](https://travis-ci.org/jhonasn/templatizator)
[![Coverage Status][coverage]](https://codecov.io/gh/jhonasn/templatizator)

This desktop app allows you to create sets of template files at some directory (that can be a project) with some differences configured with variables into the application, templatizator doesn't care about programming language or if the directory is an project.

The first motivation to create this app was by using DDD/TDD where we need to create a large set of files everytime when we create a new table for example.

The app is very configurable, the program can be used in any way you want, it only creates a set of configurable templates and save them all at the directory pointed in project field.

The app is made for windows and linux, but it can be used into mac although it's currently not tested/supported in this OS.

## How this app works?
We have only two windows in this app:
- 1. The main window:
  ![Main window picture](https://github.com/jhonasn/templatizator/raw/master/docs/resources/templatizator-window.png "Main window")
  - 1.1 Here we configure our set of templates, but first we need to choose where we'll save the templates.
  - 1.2 After that we choose the project directory, where we'll save the files of templates with variables replaced.
  - 1.3 Configure the variables that will be replaced in templates file name and content
  - 1.4 Add your templates -> go to editor window

- 2. The editor window:
  ![Editor window picture](https://github.com/jhonasn/templatizator/raw/master/docs/resources/templatizator-editor.png "Main window")
  - 2.1 Add the file name, here we can use the variables placeholders just like we use in the template content
  - 2.2 With this combo we can add the variables placeholder in file name or in the content
  - 2.3 Add the content into your template and add placeholders with the 2.2 combo
  - 2.4 This window will be used to edit your templates too

## TODO:
- [x] Change file structure to bring open just the root folder
  - [x] Save opened file tree structure when templates are saved
- [x] Change save templates in project success dialog to ask if the user wants to open the project folder
- [x] Add linux styles
- [x] Change configuration save method:
  - [x] Stop to save all in configuration json file, create a directory for every project with a unique friendly name registered in a configuration file in order to have many projects saved in the same configuration folder.
  - [x] Stop saving the entire tree node and save only the templates or relevant nodes in a separate file into the project folder, that way we can save a list of node object without children only pointing location with its path.
  - [x] Start to save variables in a separated file.
  - [x] Refactor the Configuration class into various files.
  - [x] Fix pylint warnings
  > The reason to do this is because when we change the project directory and return to the previous project we loose the previous project configuration mainly the templates.
- [x] Add an option to open and edit templates with another application
    - [x] Add context menu and add this option
- [x] Fix tkinter font icons
- [x] Add checkbox to save or not the template on project directory
    - [x] Implement to save only checked templates into the project
- [x] Add tooltip into filetree action buttons and template checkbox
- [x] Add option to add "configurable" files, those are already existing project files from any type of text file.
    - [x] Add option into context menu to add configurable files
    - [x] Implement CRUD
    - [ ] ~~Implement diff~~
    > Diff is not necessary anymore since after we save the file the template of configurable is updated too.

    > In these files we'll can put placeholders to the project templates. The editor will let the user to add all or select which templates that will be added to the file placing placeholders that will be replaced when the user save the project. After saved the configurable will continue in the project but the content will be replaced in the "template" of configurable file, reflecting the same state of original file.

  > In that way we don't need to make a new GUI nor a implementation for every type of file (for ex.: json, xml, yml, etc).
- [x] Make all strings translatable (Added languages: en, es, fr and pt_BR)
- [ ] ~~Diff project filetree folder structure~~
> Not necessary anymore since the way that templates are saved and load tree structure changed. (before the tree was saved entirely in to the program, now we just save the templates and say where they are in the tree, if the folder they are match in the tree then they are shown otherwise not)
- [x] Configure a builder script in setup.py
- [x] Add tests
- [ ] Add presentation layer tests
- [ ] Publish application into linux repository
