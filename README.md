<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [StudentSync](#studentsync)
  - [Overview](#overview)
    - [Why StudentSync](#why-studentsync)
  - [Prequisites](#prequisites)
  - [Slides](#slides)
  - [Video](#video)
  - [How to install](#how-to-install)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# StudentSync

Empower focus, Achieve more, Unleash Potential Daily 

## Overview 

StudentSync is an all-in-one productivity platform tailored for students, combining task management, habit tracking, and focus sessions into a seamless offline experience. 

It's architecture leverages a Java back end for secure data handling and a Python front end (Tkinter) for an intuitive User Interface.

### Why StudentSync

This project empowers developers to build and extend a robust, offline-capable productivity system.

The core features include :
1. **Task and Habit management**: Organize and track daily activities with CRUD (Create, Read, Update, Delete) operations and persistent storage.
2. **Secure User Authentication**: Protect user data with encrypted login and registration process.
3. **Focus and productivity tools**: Integrated Pomodoro Timers
4. **Easy to install**: Using `make` or `just`. Check [How to install](#how-to-install) for more details
5. **Offline first design**: Ensures continuous access and data integrity without internet dependency.

## Prequisites

1. Python 3.13 
2. Java OpenJDK 24 and above.


## Slides 

Use this [file](./ppt.md) and present it using `presenterm` as follows 

```bash 
presenterm -x ppt.md
```

Or you can download the PDF [file](./ppt.pdf)

## Video 


https://github.com/user-attachments/assets/c2207abb-b023-4f33-8771-b2488ef272f1


## How to install 

Clone the repository and `cd` into it.

```bash
#From Github 
git clone https://github.com/Vaishnav-Sabari-Girish/StudentSync.git

#From codeberg.org 
git clone https://codeberg.org/Vaishnav-Sabari-Girish/Student-Productivity-App.git
```

```bash
# Using make 
make build
make run 

# Using just
just build
just run
```
