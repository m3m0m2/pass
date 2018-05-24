import config


# Only this works on Ubuntu 18
def copy_xclip(text):
  import subprocess
  p = subprocess.Popen('xclip -i -sel p -f | xclip -i -sel c', stdin=subprocess.PIPE, shell=True)
  p.stdin.write(text)
  p.stdin.close()
  retcode = p.wait()
  return retcode

"""
  Neither of pyperclip nor Tkinter doesn't seem to work on Ubuntu 18
"""
def copy_pyperclip(text):
  import pyperclip
  pyperclip.copy(text)


def copy_tkinter(text):
  # Tkinter
  try:
    from Tkinter import Tk
  except ImportError:
    from tkinter import Tk
  r = Tk()
  r.withdraw()
  r.clipboard_clear()
  r.clipboard_append(text)
  r.update() # now it stays on the clipboard after the window is closed
  r.destroy()


def copy(text):
  if config.clipboard_mode == 'xclip':
    return copy_xclip(text)
  elif config.clipboard_mode == 'pyperclip':
    return copy_pyperclip(text)
  elif config.clipboard_mode == 'tkinter':
    return copy_tkinter(text)
  return None

