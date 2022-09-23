-- COMP3311 21T3 Ass2 ... extra database definitions
-- add any views or functions you need into this file
-- note: it must load without error into a freshly created mymyunsw database
-- you must submit this even if you add nothing to it

-- For q1
create or replace view studentName
as
select p.id, p.family, p.given
from people p, students s
where p.id = s.id
;

create or replace view subjectGrades(studentId, CourseCode, Term, CourseTitle, Mark, Grade, UOC)
as
select ce.student, s.code, t.code, s.name, ce.mark, ce.grade, s.uoc
from subjects s, courses c, terms t, course_enrolments ce
where s.id = c.subject
and c.term = t.id
and ce.course = c.id
order by t.code, s.code
;

-- For q2
create or replace view programRequirement
as
select r.id, p.code, r.name, r.type, ao.defby
from program_rules pr, programs p, rules r, academic_object_groups ao
where pr.program = p.id
and pr.rule = r.id
and ao.id = r.ao_group
;

create or replace view streamRequirement
as
select r.id, s.code, r.name, r.type, ao.defby
from stream_rules sr, streams s, rules r, academic_object_groups ao
where sr.stream = s.id
and sr.rule = r.id
and ao.id = r.ao_group
;
