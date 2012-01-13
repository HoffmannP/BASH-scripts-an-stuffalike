import git

baseDir = "/var/www/"
baseDir = "/home/ber/Code/SEfU/"
baseDir = "/home/ber/Desktop/TEST/"

dev, test, prod = None, None, None

def initRepros():
  return {
    'dev':  Repro(baseDir + "develop.sefu-online.de"),
    'test': Repro(baseDir + "test.sefu-online.de", {'name': "dev", 'uri': baseDir + "develop.sefu-online.de"}),
    'prod': Repro(baseDir + "www.sefu-online.de",  {'name': "dev", 'uri': baseDir + "develop.sefu-online.de"})
    }

class Tag:
  def __init__(self, tag):
    if (isinstance(tag, str) and (tag.split(".")[0] == "NoTag")):
      self.type = tag.split(".")[1]
      self.num  = ["1", "0"]
      if (tag.split(".")[1] == "Test"):
        self.num[1] = "1"
        self.num.append("0")
      self.tag = None
    else:
      tagname = tag.name
      self.type = tagname[:tagname.find("_")]
      self.num  = tagname[len(self.type)+1:].split(".")
      self.tag = tag

  def __repr__(self):
    return self.type + "_" + ".".join(self.num)

  def isType(self, type):
    return type == self.type

class Repro:
  RKey, TKey = "Release", "Test"
  
  def __init__(self, directory, remote=None):
    self.rep     = git.repo.base.Repo(directory)
    self.tags    = [Tag(tag) for tag in self.rep.tags]
    self.lastRelease = max([Tag("NoTag.Release")] + [tag for tag in self.tags if tag.isType(self.RKey)], key=lambda t:t.num)
    self.lastTest    = max([Tag("NoTag.Test")]    + [tag for tag in self.tags if tag.isType(self.TKey)], key=lambda t:t.num)
    self.remote = None
    if remote is not None:
      for rem in self.rep.remotes: 
        if (rem.name == remote["name"] and rem.url == remote["uri"]):
          self.remote = rem
      if self.remote is None:
        self.remote  = self.rep.create_remote(remote["name"], remote["uri"])

def proposeVersionUpdate():
  return dev.lastRelease.num[0:1] == dev.lastText.num[0:1]

def warn(msg):
  print "Warning: " + msg

def nextTestVersion(dev, versionUpdate):
  if dev.lastRelease.num[0:1] == dev.lastTest.num[0:1]:
    nums = dev.lastRelease.num
    if versionUpdate:
      V = [str(int(nums[0])+1), "0", "1"]
    else:
      V = [nums[0], str(int(nums[1])+1), "1"]
  else:
    nums = dev.lastTest.num
    V = [nums[0], nums[1], str(int(nums[2])+1)]
  return ".".join(V)

def test(repro, versionUpdate=False, message = None):
  dev, test = repros["dev"], repros["test"]
  v = nextTestVersion(dev, versionUpdate)
  if dev.rep.is_dirty(untracked_files=True):
    warn("development environment has uncommited or untracked files")
  next = dev.rep.create_tag(path="Test/" + v, message=message)
  test.remote.pull("master")
  test.rep.index.checkout()
  
def deploy(repro, message):
  dev, prod = repros["dev"], repros["prod"]
  v = ".".join(dev.lastTest.num[0:1])
  next = dev.create_tag(path="Release/" + v, message=message)
  prod.remote.pull("master")
  prod.rep.index.checkout()

repros = initRepros()

test(repros, message="Neu Version")
