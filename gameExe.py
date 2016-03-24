'''
Created on Feb 22, 2015

@author: edwingsantos
'''
# A simple setup script to create an executable using PyQt4. This also
# demonstrates the method for creating a Windows executable that does not have
# an associated console.
#
# PyQt4app.py is a very simple type of PyQt4 application
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application
import cx_Freeze

application_title = "Game" #what you want to application to be called
main_python_file = "intro7.py" #the name of the python file you use to run the program


from cx_Freeze import setup, Executable

executables = [cx_Freeze.Executable(main_python_file)]

cx_Freeze.setup(
        name = application_title,
        options = {"build_exe" : {"packages" : ["pygame"], "include_files":["racecar.png"]}},
        executables = executables
        )
