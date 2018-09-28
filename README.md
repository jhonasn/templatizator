# templatizator
This is desktop program to create a set of template files on some directory tree structure and save this set of files into the directory with some differences configured with variables into the application.  

The first motivation to create this app was by using DDD/TDD where we need to create a large set of files everytime when we create a new table for example.  

The app very configurable and free from programing language that you use in your system, by the way, the program can be used in any way you want, it only creates a set of configurable templates and save them all at the directory pointed in project field.  

The app is made for windows and linux, but it can be used into mac although it's currently not tested/supported in this OS.

## How this app works?
We have only two windows in this app:
- 1. The main window:  
  ![Main window picture](https://github.com/jhonasn/templatizator/raw/master/doc/img/templatizator-window.png "Main window")
  - 1.1 Here we configure our set of templates, but first we need to choose where we'll save the templates.
  - 1.2 After that we choose the project directory, where we'll save the files of templates with variables replaced.
  - 1.3 Configure the variables that will be replaced in templates file name and content
  - 1.4 Add your templates -> go to editor window
  
- 2. The editor window:  
  ![Editor window picture](https://github.com/jhonasn/templatizator/raw/master/doc/img/templatizator-editor.png "Main window")
  - 2.1 Add the file name, here we can use the variables placeholders just like we use in the template content
  - 2.2 With this combo we can add the variables placeholder in file name or in the content
  - 2.3 Add the content into your template and add placeholders with the 2.2 combo
  - 2.4 This window will be used to edit your templates too

## TODO:
- [x] Change file structure to bring open just the root folder
  - [x] Save opened file tree structure when templates are saved
- [x] Change save templates in project success dialog to ask if the user wants to open the project folder
- [x] Add linux styles
- [ ] Change configuration save method:  
  - Stop to save all in configuration json file, create a directory for every project with a unique friendly name registered in a configuration file in order to have many projects saved in the same configuration folder.  
  - Stop saving the entire tree node and save only the templates or relevant nodes in a separate file into the project folder, that way we can save a list of node object without children only pointing location with its path.  
  - Start to save variables in a separated file.  
  - Refactor the Configuration class into various files.  
  > The reason to do this is because when we change the project directory and return to the previous project we loose the previous project configuration mainly the templates.
- [ ] Add an option to open and edit templates with another application
- [ ] Add checkbox to save template on project directory
- [ ] Add option to add created files from templates into any text file with a line template with placeholders. To set location to add files, use a search into the file and then select to append or prepend the line template. Every template can use the same line template in the file or a specific template for each template.
  > In that way we don't need to make a new GUI nor a implementation for every type of file (for ex.: json, xml, yml, etc).
- [ ] Diff into configuration and project folder structure

