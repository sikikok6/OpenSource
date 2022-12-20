import git

def Commit_Crawler_File(file_name,message):
    repo = git.Repo.init()
    repo.git.add(file_name)
    repo.git.commit(m=message)
    repo.git.push()




