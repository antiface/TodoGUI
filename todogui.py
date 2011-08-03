#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import os
import sys
import re
import fileinput
import time
import datetime
import shutil

#set the directory for the todo files
TDDIR = "/home/user/Dropbox/todo/"

#global filename
filename = os.path.join(TDDIR, "todo.txt")
donefile = os.path.join(TDDIR, "done.txt")
backup = os.path.join(TDDIR, "todo.bak")
doneback = os.path.join(TDDIR, "done.bak")

#backup the todo files before we do anything
shutil.copyfile(filename, backup)
shutil.copyfile(donefile, doneback)

priorities = ["(A) ", "(B) ", "(C) ", "(D) ", "(E) "]


def add_task(task):
    todo = open(filename, 'a')
    todo.write("\n%s" % task)
    todo.close()


def archive_tasks():
    to_archive = []
    # read the data file into a list
    fin = open(filename, "r")
    task_list = fin.readlines()
    fin.close()
    for item in task_list:
        if item.startswith("X "):
            to_archive.append(item)
        if item.startswith("x "):
            to_archive.append(item)
    done = open(donefile, 'a')
    for item in to_archive:
        done.write("%s" % item)
    done.close()
    to_archive = [task.rstrip() for task in to_archive]
    for item in to_archive:
        for line in fileinput.input(filename, inplace=1):
                line = line.strip()
                if not item in line:
                    print line


def find_projects():
    global projects
    projs = []
    todo = open(filename, "r")
    projs = re.findall(r'\+\w+', todo.read())
    todo.close()
    projects = []
    [projects.append(i) for i in projs if not projects.count(i)]
    return projects


def find_contexts():
    global contexts
    conts = []
    todo = open(filename, "r")
    conts = re.findall(r'\@\w+', todo.read())
    todo.close()
    contexts = []
    [contexts.append(i) for i in conts if not contexts.count(i)]
    return contexts


def make_list():
    fin = open(filename, "r")
    global task_list
    task_list = fin.readlines()
    fin.close()
    copy_list = task_list[:]
    for item in copy_list:
        if item.startswith("x "):
            task_list.remove(item)
        if item.startswith("X "):
            task_list.remove(item)
    task_list = [task.rstrip() for task in task_list]
    task_list.sort()


class Todogui:
    def __init__(self):

        make_list()

        #make the comboboxes

        def priorityCombo(text):

            self.priority_liststore = gtk.ListStore(str)
            self.priority_combobox = gtk.ComboBox(self.priority_liststore)
            self.priority_combobox.append_text(text)
            for item in priorities:
                self.priority_liststore.append([item])
            self.cell = gtk.CellRendererText()
            self.priority_combobox.pack_start(self.cell, True)
            self.priority_combobox.add_attribute(self.cell, 'text', 0)
            self.priority_combobox.set_active(0)

        def projectCombo(text):

            find_projects()
            self.project_liststore = gtk.ListStore(str)

            def refresh_project_list():
                for project in projects:
                    self.project_liststore.append([project])
            refresh_project_list()
            self.project_combobox = gtk.ComboBox(self.project_liststore)
            self.project_combobox.prepend_text(text)
            self.cell = gtk.CellRendererText()
            self.project_combobox.pack_start(self.cell, True)
            self.project_combobox.add_attribute(self.cell, 'text', 0)
            self.project_combobox.set_active(0)

        def contextCombo(text):

            find_contexts()
            self.context_liststore = gtk.ListStore(str)

            def refresh_context_list():
                for context in contexts:
                    self.context_liststore.append([context])
            refresh_context_list()
            self.context_combobox = gtk.ComboBox(self.context_liststore)
            self.context_combobox.prepend_text(text)
            self.cell = gtk.CellRendererText()
            self.context_combobox.pack_start(self.cell, True)
            self.context_combobox.add_attribute(self.cell, 'text', 0)
            self.context_combobox.set_active(0)

        #make the task editor window
        global task_editor

        def task_editor(task, oldtask):
            self.edit_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            self.edit_window.set_transient_for(self.window)
            self.edit_window.set_position = gtk.WIN_POS_CENTER_ON_PARENT
            self.edit_window.set_size_request(500, 100)
            self.edit_window.set_title("Task editor")
            self.vbox1 = gtk.VBox()
            self.hbox1 = gtk.HBox()
            self.hbox2 = gtk.HBox()
            self.hbox3 = gtk.HBox()
            self.hbox4 = gtk.HBox()
            self.hbox5 = gtk.HBox()
            self.b1 = gtk.Button("Save task")
            self.b2 = gtk.Button("Complete task")
            self.b3 = gtk.Button("Delete task")

            priorityCombo("Add priority")
            projectCombo("Add a project")
            contextCombo("Add a context")

            self.task_entry = gtk.Entry()
            self.task_entry.set_text(task)
            self.task_entry.set_width_chars(60)
            self.label = gtk.Label("Task:")
            self.hbox1.pack_start(self.vbox1)
            self.vbox1.pack_start(self.hbox2, False)
            self.vbox1.pack_start(self.hbox3, False)
            self.vbox1.pack_start(self.hbox4, False)
            self.vbox1.pack_start(self.hbox5, False)
            self.hbox2.pack_start(self.label, False)
            self.hbox2.pack_start(self.task_entry, True)
            self.hbox3.pack_start(self.priority_combobox, False)
            self.hbox3.pack_start(self.project_combobox, False)
            self.hbox3.pack_start(self.context_combobox, False)
            self.hbox4.pack_start(self.b1, False)
            self.hbox4.pack_start(self.b2, False)
            self.hbox4.pack_start(self.b3, False)
            self.label2 = gtk.Label("Add new projects with + and new"
            " contexts with @")
            self.hbox5.pack_start(self.label2, False)

            self.edit_window.add(self.hbox1)
            self.edit_window.show_all()

            #callbacks for task editor
            self.b1.connect("clicked", self.addthistask, oldtask)
            self.b2.connect("clicked", self.complete_task, None)
            self.b3.connect("clicked", self.delete_task, None)
            self.priority_combobox.connect("changed", self.pri_b1_changed)
            self.project_combobox.connect("changed", self.pro_b1_changed)
            self.context_combobox.connect("changed", self.cont_b1_changed)

        #setup the GUI
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(600, 500)
        self.window.connect("destroy", lambda w: gtk.main_quit())
        self.window.set_title("Todo list")
        self.mb = gtk.MenuBar()
        self.filemenu = gtk.Menu()
        self.filem = gtk.MenuItem("List options")
        self.filem.set_submenu(self.filemenu)
        self.refreshfile = gtk.MenuItem("Refresh list")
        self.filemenu.append(self.refreshfile)
        self.archive = gtk.MenuItem("Archive completed tasks")
        self.filemenu.append(self.archive)
        self.mb.append(self.filem)

        def archiver(activate):
            archive_tasks()
        self.archive.connect("activate", archiver)
        self.liststore = gtk.ListStore(str)
        self.list_tasks(task_list)
        self.treeview = gtk.TreeView(self.liststore)
        self.rendererText = gtk.CellRendererText()
        self.taskcolumn = gtk.TreeViewColumn("Task", self.rendererText, text=0)
        self.taskcolumn.set_sort_column_id(1)
        self.treeview.append_column(self.taskcolumn)
        self.scroll1 = gtk.ScrolledWindow()
        self.scroll1.add(self.treeview)
        self.addlabel = gtk.Label("Add a new task +project @context:")
        self.quickadd = gtk.Entry()
        self.quickadd.set_width_chars(40)
        self.search_tasks = gtk.Entry()
        self.search_tasks.set_text("Search tasks")
        self.vbox1 = gtk.VBox()
        self.hbox1 = gtk.HBox()
        self.hbox2 = gtk.HBox()
        self.hbox3 = gtk.HBox()
        self.hbox4 = gtk.HBox()
        self.b1 = gtk.Button("Add new task")

        #b2 = gtk.Button("Refresh list")
        #b2.connect("clicked", refresh_button, None)
        #b3 = gtk.Button("Archive done tasks")
        #b3.connect("clicked", archive_button, None)
        self.b4 = gtk.Button("Complete selected task")

        priorityCombo("Filter by priority")
        projectCombo("Filter by project")
        contextCombo("Filter by context")

        self.vbox1.pack_start(self.mb, False, False, 0)
        self.hbox1.pack_start(self.vbox1)
        self.vbox1.pack_start(self.hbox2, False)
        self.vbox1.pack_start(self.hbox3, False)
        self.vbox1.pack_start(self.hbox4, False)
        self.hbox2.pack_start(self.priority_combobox, False)
        self.hbox2.pack_start(self.project_combobox, False)
        self.hbox2.pack_start(self.context_combobox, False)
        self.hbox2.pack_start(self.search_tasks, True)
        self.hbox3.pack_start(self.b1, False)
        self.hbox3.pack_start(self.b4, False)
        self.hbox4.pack_start(self.addlabel, False)
        self.hbox4.pack_start(self.quickadd, True)
        self.vbox1.pack_start(self.scroll1)

        self.window.add(self.hbox1)
        self.window.show_all()

        #callbacks for main window
        self.archive.connect("activate", archiver)
        self.treeview.connect('row-activated', self.edit_task_tree)
        self.refreshfile.connect("activate", self.refreshes_list)
        self.priority_combobox.connect("changed", self.pri_c_b_changed)
        self.project_combobox.connect("changed", self.proj_c_b_changed)
        self.context_combobox.connect("changed", self.cont_combo_box_changed)
        self.search_tasks.connect("activate", self.searchtasks)
        self.quickadd.connect("activate", self.quickaddtask)
        self.b1.connect("clicked", self.add_new_task, None)
        self.b4.connect("clicked", self.complete_button, None)

    def edit_task_tree(self, treeview, path, column):
        model = self.treeview.get_model()
        iter = model.get_iter(path)
        task = model.get_value(iter, 0)
        global oldtask
        oldtask = task
        task_editor(task, oldtask)

    def task_complete(self, task):
        if re.match(r'\A\(', task):
            task = task[4:]
        date = str(datetime.date.today())
        completedtask = "x " + date + " " + task
        message = "Complete task: %s" % (task)
        md = gtk.MessageDialog(None,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, message)
        response = md.run()
        md.destroy()
        if response == gtk.RESPONSE_YES:
            for line in fileinput.input(filename, inplace=1):
                line = line.strip()
                if not task in line:
                    print line
                else:
                    print completedtask
            self.refresh_list()

    def task_delete(self, task):
        message = "Are you sure you want to delete the task: %s" % (task)
        md = gtk.MessageDialog(None,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, message)
        response = md.run()
        md.destroy()
        if response == gtk.RESPONSE_YES:
            for line in fileinput.input(filename, inplace=1):
                line = line.strip()
                if task != line:
                    print line
        self.refresh_list()

    def addthistask(self, widget, data=None):
        task = (self.task_entry.get_text())
        if oldtask != "---":
            for line in fileinput.input(filename, inplace=1):
                line = line.strip()
                if not oldtask in line:
                    print line
        add_task(task)
        self.refresh_list()
        self.edit_window.destroy()

    def complete_task(self, widget, data=None):
        task = (self.task_entry.get_text())
        self.task_complete(task)
        self.edit_window.destroy()

    def delete_task(self, widget, data=None):
        task = (self.task_entry.get_text())
        self.task_delete(task)
        self.edit_window.destroy()

    def priority_add(self, priority_to_add):
        task = (self.task_entry.get_text())
        if re.match(r'\A\(', task):
            task = task[4:]
        task = (priority_to_add + task)
        self.task_entry.set_text(task)

    def pri_b1_changed(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        priority_to_add = model.get_value(iter, 0)
        self.priority_add(priority_to_add)

    def add_new_project(self, project_to_add):
        task = (self.task_entry.get_text())
        task = (task + " " + project_to_add)
        self.task_entry.set_text(task)

    def pro_b1_changed(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        project_to_add = model.get_value(iter, 0)
        self.add_new_project(project_to_add)

    def add_new_context(self, context_to_add):
        task = (self.task_entry.get_text())
        task = (task + " " + context_to_add)
        self.task_entry.set_text(task)

    def cont_b1_changed(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        context_to_add = model.get_value(iter, 0)
        self.add_new_context(context_to_add)

    def list_tasks(self, task_list):
        for task in task_list:
            self.liststore.append([task])

    def refresh_list(self):
        for line in fileinput.input(filename, inplace=1):
            line = line.strip()
            if line != '':
                print line
        self.liststore.clear()
        make_list()
        self.list_tasks(task_list)
        find_projects()
        self.project_liststore.clear()
        self.refresh_project_list()
        find_contexts()
        self.context_liststore.clear()
        self.refresh_context_list()

    def filter_list_priority(self, priority_to_find, task_list):
        task_list = [item for item in task_list if priority_to_find in item]
        self.liststore.clear()
        self.list_tasks(task_list)
        self.project_combobox.set_active(0)
        self.context_combobox.set_active(0)
        self.search_tasks.set_text("Search tasks")

    def refreshes_list(self, activate):
        self.refresh_list()

    def pri_c_b_changed(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        priority_to_find = model.get_value(iter, 0)
        self.filter_list_priority(priority_to_find, task_list)

    def filter_list_project(self, project_to_find, task_list):
        task_list = [item for item in task_list if project_to_find in item]
        self.liststore.clear()
        self.list_tasks(task_list)
        self.context_combobox.set_active(0)
        self.priority_combobox.set_active(0)
        self.search_tasks.set_text("Search tasks")

    def refresh_project_list(self):
        for project in projects:
            self.project_liststore.append([project])
        self.project_combobox.prepend_text('Filter by project')
        self.project_combobox.set_active(0)

    def proj_c_b_changed(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        project_to_find = model.get_value(iter, 0)
        if project_to_find != "Filter by project":
            self.filter_list_project(project_to_find, task_list)

    def filter_list_context(self, context_to_find, task_list):
        task_list = [item for item in task_list if context_to_find in item]
        self.liststore.clear()
        self.list_tasks(task_list)
        self.project_combobox.set_active(0)
        self.priority_combobox.set_active(0)
        self.search_tasks.set_text("Search tasks")

    def refresh_context_list(self):
        for context in contexts:
            self.context_liststore.append([context])
        self.context_combobox.prepend_text('Filter by context')
        self.context_combobox.set_active(0)

    def cont_combo_box_changed(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        context_to_find = model.get_value(iter, 0)
        if context_to_find != "Filter by context":
            self.filter_list_context(context_to_find, task_list)

    def searchfortask(self, task_list, tofind):
        temp_list = task_list
        filtered = []
        for item in temp_list:
            if item.find(tofind) != -1:
                filtered.append(item)
        task_list = filtered
        self.liststore.clear()
        self.list_tasks(task_list)
        self.context_combobox.set_active(0)
        self.priority_combobox.set_active(0)
        self.project_combobox.set_active(0)

    def searchtasks(self, widget):
        tofind = self.search_tasks.get_text()
        self.searchfortask(task_list, tofind)

    def quickaddtask(self, widget):
        task = self.quickadd.get_text()
        add_task(task)
        self.refresh_list()
        self.quickadd.set_text("")

    def add_new_task(self, widget, data=None):
        task = ""
        global oldtask
        oldtask = "---"
        task_editor(task, oldtask)

    def archive_button(self, widget, data=None):
        archive_tasks()

    def complete_button(self, widget, data=None):
        path, focuscolumn = self.treeview.get_cursor()
        model = self.treeview.get_model()
        iter = model.get_iter(path)
        task = model.get_value(iter, 0)
        self.task_complete(task)

    def main(self):
        gtk.main()

if __name__ == "__main__":
    todo = Todogui()
    todo.main()
