# py-wsgi-db-app

A python app for generating quick web applications

## Overview

This tool is intended to take a database definition and create the database and start running a wsgi application allowing 
users to manage the content of that database, with no further coding.

Additionally, this tool can be used as a starting point for building more complex python web interfaces for database backends.

## Components 

The scripts needed to run this application are:

1. Generic database functions: A set of functions to interact directly with the database
2. App-specific database functions: Wrappers for generic db functions to make them more easily understood in the rest of the app
3. Generic HTML functions: A set of functions objects used to create HTML responses 
4. App-specific HTML functions: Functions that create pages specific to the application, using the generic HTML objects
5. Generic Javascript functions: A set of functions used for autocomplete, form validation, and table sorting
6. Main app script: Used to create the webserver and handle all requests
