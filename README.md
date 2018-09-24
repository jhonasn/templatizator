# templatizator
A desktop program to create a set of template files on some directory tree structure and save this set of files into the directory with some differences configured with variables into the application. The first motivation to create this app was by using DDD/TDD where we need to create a large set of files everytime when we create a new table for example. The app very configurable and free from programing language that you use in your system, by the way the program can be used in any way you want, it only creates a set of configurable templates and save them all at the directory pointed in project field.

## How this app works?
We have only two windows in this app:
- 1. The main window:
  - [img]
  - 1.1 Here we configure our set of templates, but first we need to choose where we'll save the templates.
  - 1.2 After that we choose the project directory, where we'll save the files of templates with variables replaced.
  - 1.3 Configure the variables that will be replaced in templates file name and content
  - 1.4 Add your templates -> go to editor window
  
- 2. The editor window:
  - [img]
  - 2.1 Add the file name, here we can use the variables placeholders just like we use in the template content
  - 2.2 With this combo we can add the variables placeholder in file name or in the content
  - 2.3 Add the content into your template and add placeholders with the 2.2 combo
  - 2.4 This window will be used to edit your templates too

## TODO:
- [ ] Change file structure to bring open just the root folder
- [ ] Change save templates in project success dialog to ask if the user wants to open the project folder
- [ ] Add option to add created files from templates into xml (csproj) or json files
- [ ] Diff into configuration and project folder structure
