# COMP3311 21T3 Ass2 ... Python helper functions
# add here any functions to share between Python scripts 
# you must submit this even if you add nothing

def getProgram(db,code):
  cur = db.cursor()
  cur.execute("select * from Programs where code = %s",[code])
  info = cur.fetchone()
  cur.close()
  if not info:
    return None
  else:
    return info

def getStream(db,code):
  cur = db.cursor()
  cur.execute("select * from Streams where code = %s",[code])
  info = cur.fetchone()
  cur.close()
  if not info:
    return None
  else:
    return info

def getDefultProgram(db,zid):
  cur = db.cursor()
  query = """
    select p.id, p.code, p.name, p.uoc, p.offeredby, p.career, p.duration, p.description
    from program_enrolments pe, programs p
    where pe.program = p.id
    and pe.student = %s
    order by pe.term DESC
    ;
    """
  cur.execute(query, [zid])
  info = cur.fetchone()
  cur.close()
  if not info:
    return None
  else:
    return info

def getDefultStream(db,zid):
  cur = db.cursor()
  query = """
    select s.id, s.code, s.name, s.offeredby, s.stype, s.description
    from stream_enrolments se, program_enrolments pe, streams s
    where se.partof = pe.id
    and se.stream = s.id
    and pe.student = %s
    order by pe.term DESC
    ;
    """
  cur.execute(query, [zid])
  info = cur.fetchone()
  cur.close()
  if not info:
    return None
  else:
    return info

def getStudent(db,zid):
  cur = db.cursor()
  qry = """
  select p.*, c.name
  from   People p
         join Students s on s.id = p.id
         join Countries c on p.origin = c.id
  where  p.id = %s
  """
  cur.execute(qry,[zid])
  info = cur.fetchone()
  cur.close()
  if not info:
    return None
  else:
    return info



# For q2
def programRequirement(db, program):
  query = """
  select id, name, type, defby
  from programRequirement
  where code = %s
  ;
  """
  cur = db.cursor()
  cur.execute(query, [program])
  for tuple in cur.fetchall():
    ruleId, ruleName, ruleType, ruleDefby = tuple
    if ruleType == 'DS':
      DS(db, ruleName, ruleId)
    elif ruleType == 'CC':
      CC(db, ruleName, ruleId)
    elif ruleType == 'PE':
      PE(db, ruleName, ruleId, ruleDefby)
    elif ruleType == 'FE':
      FE(db, ruleId)
    elif ruleType == 'GE':
      GE()


def streamRequirement(db, stream):
  query = """
  select id, name, type, defby
  from streamRequirement
  where code = %s
  ;
  """
  cur = db.cursor()
  cur.execute(query, [stream])
  for tuple in cur.fetchall():
    ruleId, ruleName, ruleType, ruleDefby = tuple
    if ruleType == 'DS':
      DS(db, ruleName, ruleId)
    elif ruleType == 'CC':
      CC(db, ruleName, ruleId)
    elif ruleType == 'PE':
      PE(db, ruleName, ruleId, ruleDefby)
    elif ruleType == 'FE':
      FE(db, ruleId)
    elif ruleType == 'GE':
      GE()


def printMinMax(db, ruleId):
  query = """
  select min_req, max_req
  from rules
  where id = %s
  """
  cur = db.cursor()
  cur.execute(query, [ruleId])
  min_req, max_req = cur.fetchone()
  if max_req == None and min_req == None:
    return ''
  elif max_req == None:
    return 'at least ' + str(min_req)
  elif min_req == None:
    return 'up to ' + str(max_req)
  elif min_req < max_req:
    return 'between ' + str(min_req) + ' and ' + str(max_req)
  elif min_req == max_req:
    return str(min_req)


def DS(db, ruleName, ruleId):
  print(printMinMax(db, ruleId), 'stream(s) from', ruleName)

  query = """
  select definition
  from rules r, academic_object_groups ao
  where ao.id = r.ao_group
  and r.id = %s
  """
  cur = db.cursor()
  cur.execute(query, [ruleId])
  streams = cur.fetchone()[0]
  streams = streams.split(',')
  for code in streams:
    streamName(db, code)
      
      
def CC(db, ruleName, ruleId):
  query = """
  select definition
  from rules r, academic_object_groups ao
  where ao.id = r.ao_group
  and r.id = %s
  """
  cur = db.cursor()
  cur.execute(query, [ruleId])
  courses = cur.fetchone()[0]
  courses = courses.split(',')
  if len(courses) == 1:
    print(ruleName)
  else:
    print('all courses from', ruleName)
    
  for code in courses:
    # Alternatives
    if code[0] == '{' and code[-1] == '}':
      code = code[1:-1].split(';')
      courseName(db, code[0])
      del code[0]

      for alternativeCode in code:
        alternativeCourseName(db, alternativeCode)
    # Normal course
    else:
      courseName(db, code)


def PE(db, ruleName, ruleId, ruleDefby):
  print(printMinMax(db, ruleId), 'UOC courses from', ruleName)

  query = """
  select definition
  from rules r, academic_object_groups ao
  where ao.id = r.ao_group
  and r.id = %s
  """
  cur = db.cursor()
  cur.execute(query, [ruleId])
  courses = cur.fetchone()[0]

  if ruleDefby == 'enumerated':
    courses = courses.split(',')
    for code in courses:
      courseName(db, code)

  elif ruleDefby == 'pattern':
    print('- courses matching', courses)


def FE(db, ruleId):
  print(printMinMax(db, ruleId), 'UOC of Free Electives')


def GE():
  print('12 UOC of General Education')


def streamName(db, code):
  query = """
  select name
  from streams
  where code = %s
  """
  cur = db.cursor()
  cur.execute(query, [code])
  name = cur.fetchone()
  if name == None:
    name = '???'
  else:
    name = name[0]
  print('-', code, name)


def courseName(db, code):
  query = """
  select name
  from subjects
  where code = %s
  """
  cur = db.cursor()
  cur.execute(query, [code])
  name = cur.fetchone()
  if name == None:
    name = '???'
  else:
    name = name[0]
  print('-', code, name)


def alternativeCourseName(db, alternativeCode):
  query = """
  select name
  from subjects
  where code = %s
  """
  cur = db.cursor()
  cur.execute(query, [alternativeCode])
  name = cur.fetchone()
  if name == None:
    name = '???'
  else:
    name = name[0]
    print('  or', alternativeCode, name)



# For q3
def getCCDict(db, ruleName, ruleId):
  query = """
  select definition
  from rules r, academic_object_groups ao
  where ao.id = r.ao_group
  and r.id = %s
  """
  cur = db.cursor()
  cur.execute(query, [ruleId])
  courses = cur.fetchone()[0]
  courses = courses.split(',')
  return {'name': ruleName, 'courses': courses}


def getPEDict(db, ruleName, ruleId, ruleDefby):
  query = """
  select definition, r.min_req, r.max_req
  from rules r, academic_object_groups ao
  where ao.id = r.ao_group
  and r.id = %s
  """
  cur = db.cursor()
  cur.execute(query, [ruleId])
  courses, min_req, max_req = cur.fetchone()
  courses = courses.split(',')

  return {'name': ruleName, 'min': min_req,'max': max_req,'defBy': ruleDefby,'courses': courses}


def getFEDict(db, ruleId):
  query = """
  select min_req, max_req
  from rules
  where id = %s
  """
  cur = db.cursor()
  cur.execute(query, [ruleId])
  min_req, max_req = cur.fetchone()
  return {'min': min_req,'max': max_req}


def getGEDict():
  return {'min': 12,'max': 12}


def createRules(db, code):
  query = ''
  if len(code) == 4:
    query = """
    select id, name, type, defby
    from programRequirement
    where code = %s
    ;
    """
  elif len(code) == 6:
    query = """
    select id, name, type, defby
    from streamRequirement
    where code = %s
    ;
    """

  cur = db.cursor()
  cur.execute(query, [code])
  rule = {
    'CC': [], 
    'PE': [], 
    'FE': None,
    'GE': None,
  }
  for tuple in cur.fetchall():
    ruleId, ruleName, ruleType, ruleDefby = tuple
    if ruleType == 'CC':
      rule[ruleType].append(getCCDict(db, ruleName, ruleId))
    elif ruleType == 'PE':
      rule[ruleType].append(getPEDict(db, ruleName, ruleId, ruleDefby))
    elif ruleType == 'FE':
      rule[ruleType] = getFEDict(db, ruleId)
    elif ruleType == 'GE':
      rule[ruleType] = getGEDict()

  return rule


def completeCourse(courseCode, rule):
  for aoGroup in rule['CC']:
    for c in aoGroup['courses']:
      if courseCode == c:
        aoGroup['courses'].remove(c)
        return ('CC', aoGroup['name'])
      elif c[0] == '{' and c[-1] == '}':
        alternativeC = c[1:-1].split(';')
        if courseCode in alternativeC:
          aoGroup['courses'].remove(c)
          return ('CC', aoGroup['name'])

  for aoGroup in rule['PE']:
    for c in aoGroup['courses']:
      if aoGroup['defBy'] == 'enumerated':
        if courseCode == c:
          aoGroup['courses'].remove(c)
          return ('PE', aoGroup['name'])
        elif c[0] == '{' and c[-1] == '}':
          alternativeC = c[1:-1].split(';')
          if courseCode in alternativeC:
            aoGroup['courses'].remove(c)
            return ('PE', aoGroup['name'])

      elif aoGroup['defBy'] == 'pattern':
        if courseCode[:5] == c[:5]:
          return ('PE', aoGroup['name'])
  
  if courseCode[:3] == 'GEN':
    return ('GE', 'General Education')
  
  return ('FE', 'Free Electives')


def matchAOGroup(cType, aName, progRule, strmRule, totalAchievedUOC, UOC, towards):
  if cType == 'CC':
    return matchCC(aName, totalAchievedUOC, UOC, towards)
  if cType == 'PE':
    return matchPE(cType, aName, progRule, strmRule, totalAchievedUOC, UOC, towards)
  if cType == 'GE':
    return matchGE(aName, progRule, strmRule, totalAchievedUOC, UOC, towards)
  if cType == 'FE':
    return matchFE(progRule, strmRule, totalAchievedUOC, UOC, towards)

  return (totalAchievedUOC, UOC, towards)


def matchCC(aName, totalAchievedUOC, UOC, towards):
  totalAchievedUOC += UOC
  UOC = str(UOC) + 'uoc'
  towards = aName
  return (totalAchievedUOC, UOC, towards)

def matchPE(cType, aName, progRule, strmRule, totalAchievedUOC, UOC, towards):
  for aoGroup in progRule[cType]:
    if aoGroup['name'] == aName:
      if earnCredit[aoGroup]:
        totalAchievedUOC += UOC
        UOC = str(UOC) + 'uoc'
        towards = aName
        return (totalAchievedUOC, UOC, towards)
  for aoGroup in strmRule[cType]:
    if aoGroup['name'] == aName:
      if earnCredit(aoGroup, UOC):
        totalAchievedUOC += UOC
        UOC = str(UOC) + 'uoc'
        towards = aName
        return (totalAchievedUOC, UOC, towards)
  return matchFE(progRule, strmRule, totalAchievedUOC, UOC, towards)

def matchGE(aName, progRule, strmRule, totalAchievedUOC, UOC, towards):
  if earnCredit(progRule['GE'], UOC):
    totalAchievedUOC += UOC
    UOC = str(UOC) + 'uoc'
    towards = aName
  elif earnCredit(strmRule['GE'], UOC):
    totalAchievedUOC += UOC
    UOC = str(UOC) + 'uoc'
    towards = aName
  else:
    return matchFE(progRule, strmRule, totalAchievedUOC, UOC, towards)
  return (totalAchievedUOC, UOC, towards)

def matchFE(progRule, strmRule, totalAchievedUOC, UOC, towards):
  if earnCredit(progRule['FE'], UOC):
    totalAchievedUOC += UOC
    UOC = str(UOC) + 'uoc'
    towards = 'Free Electives'
  elif earnCredit(strmRule['FE'], UOC):
    totalAchievedUOC += UOC
    UOC = str(UOC) + 'uoc'
    towards = 'Free Electives'
  else:
    UOC = '0uoc'
    towards = 'does not satisfy any rule'
  return (totalAchievedUOC, UOC, towards)
    
def earnCredit(aoGroup, UOC):
  if aoGroup != None:
    if aoGroup['min'] != None and aoGroup['max'] != None:
      if aoGroup['min'] - UOC >= 0 and aoGroup['max'] - UOC >= 0:
        aoGroup['min'] -= UOC
        if aoGroup['min'] == 0:
          aoGroup['min'] = None
        aoGroup['max'] -= UOC
        if aoGroup['max'] == 0:
          aoGroup['max'] = None
        return True
    elif aoGroup['min'] != None:
      if aoGroup['min'] - UOC >= 0:
        aoGroup['min'] -= UOC
        if aoGroup['min'] == 0:
          aoGroup['min'] = None
        return True
    elif aoGroup['max'] != None:
      if aoGroup['max'] - UOC >= 0:
        aoGroup['max'] -= UOC
        if aoGroup['max'] == 0:
          aoGroup['max'] = None
        return True
  return False


def printToComplete(db, strmRule, progRule):
  CCToComplete(db, strmRule['CC'])
  CCToComplete(db, progRule['CC'])
  PEToComplete(strmRule['PE'])
  PEToComplete(progRule['PE'])
  GEToComplete(progRule['GE'], strmRule['GE'])
  FEToComplete(progRule['FE'], strmRule['FE'])

def CCToComplete(db, CCList):
  for aoGroup in CCList:
    for code in aoGroup['courses']:
      # Alternatives
      if code[0] == '{' and code[-1] == '}':
        code = code[1:-1].split(';')
        courseName(db, code[0])
        del code[0]

        for alternativeCode in code:
          alternativeCourseName(db, alternativeCode)
      # Normal course
      else:
        courseName(db, code)

def PEToComplete(PEList):
  for aoGroup in PEList:
    if aoGroup['min'] == 0:
      aoGroup['min'] = None
    if aoGroup['max'] == 0:
      aoGroup['max'] = None
    if aoGroup['min'] != None or aoGroup['max'] != None:
      print(printMinMaxWithNum(aoGroup['min'], aoGroup['max']), 'UOC courses from', aoGroup['name'])

def GEToComplete(progGE, strmGE):
  min_req = 0
  max_req = 0
  if progGE != None:
    if progGE['min'] != None:
      min_req += progGE['min']
    if progGE['max'] != None:
      max_req += progGE['max']
  if strmGE != None:
    if strmGE['min'] != None:
      min_req += strmGE['min']
    if strmGE['max'] != None:
      max_req += strmGE['max']

  if min_req == 0:
    min_req = None
  if max_req == 0:
    max_req = None
  if min_req != None or max_req != None:
    print(printMinMaxWithNum(min_req, max_req), 'UOC of General Education')

def FEToComplete(progFE, strmFE):
  min_req = 0
  max_req = 0
  if progFE != None:
    if progFE['min'] != None:
      min_req += progFE['min']
    if progFE['max'] != None:
      max_req += progFE['max']
  if strmFE != None:
    if strmFE['min'] != None:
      min_req += strmFE['min']
    if strmFE['max'] != None:
      max_req += strmFE['max']

  if min_req == 0:
    min_req = None
  if max_req == 0:
    max_req = None
  if min_req != None or max_req != None:
    print(printMinMaxWithNum(min_req, max_req), 'UOC of Free Electives')

def printMinMaxWithNum(min_req, max_req):
  if max_req == None and min_req == None:
    return ''
  elif max_req == None:
    return 'at least ' + str(min_req)
  elif min_req == None:
    return 'up to ' + str(max_req)
  elif min_req < max_req:
    return 'between ' + str(min_req) + ' and ' + str(max_req)
  elif min_req == max_req:
    return str(min_req)