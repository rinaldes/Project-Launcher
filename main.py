from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
import subprocess
import time

class Launcher(Extension):
  def __init__(self):
    super().__init__()
    self.subscribe(KeywordQueryEvent, ProjectFinder())

class ProjectFinder(EventListener):
  def __init__(self):
    self._last_search_time = 0
    self._last_results = []
    self._cached_projects = []
    self._last_cache_time = 0

  def _get_projects(self, ext):
    current_time = time.time()
    
    # Get customizable preferences with fallbacks
    cache_duration = int(ext.preferences.get("cache_duration", "30"))
    search_depth = int(ext.preferences.get("search_depth", "4"))
    folder = ext.preferences["folder"]
    
    if current_time - self._last_cache_time < cache_duration:
      return self._cached_projects
      
    try:
      cmd = f"fd -H '^.git$' -t d -d {search_depth} {folder} --exec dirname"
      self._cached_projects = subprocess.check_output(cmd, shell=True, text=True).splitlines()
    except subprocess.CalledProcessError:
      cmd = f"find {folder} -maxdepth {search_depth} -type d -name .git -prune -exec dirname {{}} \;"
      try:
        self._cached_projects = subprocess.check_output(cmd, shell=True, text=True).splitlines()
      except subprocess.CalledProcessError:
        self._cached_projects = []
    
    self._last_cache_time = current_time
    return self._cached_projects

  def on_event(self, event, ext):
    current_time = time.time()
    
    # Get customizable preferences with fallbacks
    debounce_delay = float(ext.preferences.get("debounce_delay", "0.4"))
    max_results = int(ext.preferences.get("max_results", "10"))
    
    if current_time - self._last_search_time < debounce_delay:
      return RenderResultListAction(self._last_results)
    
    self._last_search_time = current_time
    projects = self._get_projects(ext)
    
    search_term = event.get_argument()
    if search_term:
      search_term = search_term.lower()
      projects = [p for p in projects if search_term in p.lower()][:max_results]
    else:
      projects = projects[:max_results]

    items = [
      ExtensionResultItem(
        icon='images/icon.png',
        name=project.split('/')[-1],
        description=project,
        on_enter=RunScriptAction(f"{ext.preferences['editor']} {project}")
      ) for project in projects
    ]

    if not items:
      items.append(ExtensionResultItem(
        icon='images/icon.png',
        name='No projects found',
        description='No projects found in the specified folder',
        on_enter=HideWindowAction()
      ))

    self._last_results = items
    return RenderResultListAction(items)

if __name__ == '__main__':
  Launcher().run()
