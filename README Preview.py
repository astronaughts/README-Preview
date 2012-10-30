import sublime
import sublime_plugin
import os
import json
import urllib2
import tempfile
import webbrowser

readme_pattern = [
    'readme',
    'readme.md',
    'readme.markdown',
]

def get_dirs(path):
    dirs = []
    for item in os.listdir(path):
        if os.path.isdir(os.path.join(path, item)):
            dirs.append(item)
    return dirs

def get_readme_path(path):
    for item in os.listdir(path):
        for pattern in readme_pattern:
            if item.lower() == pattern:
                return os.path.join(path, item)

def build_html(contents):
    html = u'<!DOCTYPE html><html><head><meta charset="utf-8">'
    html += '<link href="http://kevinburke.bitbucket.org/markdowncss/markdown.css" rel="stylesheet"></link>'
    html += '</head><body>'
    html += contents
    html += '</body>'
    return html

class ReadmePreviewCommand(sublime_plugin.TextCommand):
    readmes = {}

    def run(self, edit):
        path = sublime.packages_path()
        for item in get_dirs(path):
            readme_path = get_readme_path(os.path.join(path, item))
            if readme_path:
                self.readmes[item] = readme_path

        self.view.window().show_quick_panel(self.readmes.keys(), self.open)

    def open(self, index):
        try:
            packages = self.readmes.keys()
            package_paths = self.readmes.values()

            contents = open(package_paths[index]).read()
            data = json.dumps({ 'text': contents, 'mode': 'gfm' })
            html = urllib2.urlopen('https://api.github.com/markdown', data).read().decode('utf-8')

            tmp_path = os.path.join(tempfile.gettempdir(), '%s.html' % packages[index])
            tmp_html = open(tmp_path, 'w')
            tmp_html.write(build_html(html))
            tmp_html.close()

            webbrowser.open('file://' + tmp_path, 1, True)
            sublime.status_message('open %s README file' % packages[index])

        except Exception as e:
            sublime.error_message('ReadMe [Error]: Could not open README.')