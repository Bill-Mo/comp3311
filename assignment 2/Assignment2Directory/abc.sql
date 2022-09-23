create or replace view q1(program, course)
as
select *
from rules r, academic_object_groups ao
where ao.id = r.ao_group
--and r.type = 'CC'
;

create or replace view q2(studentId, CourseCode, Term, CourseTitle, Mark, Grade, UOC)
as
select ce.student, s.code, t.code, s.name, ce.mark, ce.grade, s.uoc
from subjects s, courses c, terms t, course_enrolments ce
where s.id = c.subject
and c.term = t.id
and ce.course = c.id
order by t.code, s.code
;

create or replace view q3
as
select pr.program, r.name
from rules r, program_rules pr
where r.id = pr.rule
;

create or replace view q4(streamCode, streamName, offeredby, ruleName, min, max, groupType, groupDefby, groupDef)
as
select s.code, s.name, o.longname, r.name, r.min_req, r.max_req, ao.type, ao.defby, ao.definition
from stream_rules sr, streams s, orgunits o, rules r, academic_object_groups ao
where sr.stream = s.id
and sr.rule = r.id
and s.offeredby = o.id
and ao.id = r.ao_group
--and s.code = 'AEROAH'
;

create or replace view q5(programCode, programName, offeredby, ruleName, ruleType, min, max, groupType, groupDefby, groupDef)
as
select p.code, p.name, o.longname, r.name, r.type, r.min_req, r.max_req, ao.type, ao.defby, ao.definition
from program_rules pr, programs p, orgunits o, rules r, academic_object_groups ao
where pr.program = p.id
and pr.rule = r.id
and p.offeredby = o.id
and ao.id = r.ao_group
--and p.code = '8543'
and ao.id = '686014'
;

create or replace view q6(programCode, ruleName, ruleType, min, max, groupType, groupDefby, groupDef)
as
select p.code, r.name, r.type, r.min_req, r.max_req, ao.type, ao.defby, ao.definition
from program_rules pr, programs p, orgunits o, rules r, academic_object_groups ao
where pr.program = p.id
and pr.rule = r.id
and p.offeredby = o.id
and ao.id = r.ao_group
;

create or replace view q7
as
select s.id, s.code, s.name, s.offeredby, s.stype, s.description, pe.term
from stream_enrolments se, program_enrolments pe, streams s
where se.partof = pe.id
and se.stream = s.id
--and pe.student = 5123788
order by pe.term DESC
;

