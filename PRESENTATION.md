# Rockstar Interpreter 

## Introduction 

Esoteric languages are languages that are designed to obfuscate the meaning of the program it represents. They were created to challenge the norms
of what a typical programming language is supposed to look like. Esolangs are kind of an example of steganography in that way. 

## What is rockstar? 
[Rockstar Home](https://codewithrockstar.com/) 
Pasted is the website of the rockstar language we have created an interpreter for. In it contains a documentation page that extensively describes the function of each word in the program and how these words come 
together to create an actual programming language. 

The words used in the rockstar programming language are based on lyrics to "1980s hard rock and power ballads." This makes for a beautifully poetic language that can also do things that you might want to do in a language 
like python or Java. 

## What does it do? 
Our goal was to write a script that could parse through the rockstar esoteric language, make sense of its statements, and produce an output based on the rockstar code. 

In order to do this, our script is split up into two main functions, each of course with their own sub-sections and parts that required seperate attention. 

First, the script parses through the code, line by line, and generates an action dictionary based on each line or "statement" which would have a keyword associated with it like "print" or "assign variable" which would be 
indicative of what that line in the rockstar code is doing. 

Second, in order to produce the outcome expected from the rockstar code, these action dictionaries need to be interpreted. We loop through these action dictionaries, constructed in the first part, and produce what these 
action dictionaries describe. 

## Printing 
print, whisper, shout 
print true 
print 1
print "hello world"
print null

## Variable Assignment 
<var> is <exp>
let <var> be <exp>
put <exp> into <var>

## Poetic Numbers
cheese is a symphonic melody. => cheese = 196

## Arithmetic 
in place arithmetic
rockstar has some cool features for arithmetic

## Conditionals
if conditional print stuff

## Lists
the main interface for using lists is rock 


