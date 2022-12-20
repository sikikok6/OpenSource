import git

repo = git.Repo.init()
repo.git.add(".")
repo.git.commit(m='test_here')
repo.git.push()


