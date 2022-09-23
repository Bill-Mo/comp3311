-- COMP3311 21T3 Assignment 1
--
-- Fill in the gaps ("...") below with your code
-- You can add any auxiliary views/function that you like
-- The code in this file MUST load into a database in one pass
-- It will be tested as follows:
-- createdb test; psql test -f ass1.dump; psql test -f ass1.sql
-- Make sure it can load without errorunder these conditions

-- For Q5
create or replace view styleCount(style, num)
as
select s.name, count(*)
from beers b, styles s
where b.style = s.id
group by s.id
;

-- For Q8
create or replace view mostBreweries(city, num)
as
select metro, count(metro)
from locations l, breweries b
where l.id = b.located_in
group by metro
;

-- For Q10 and Q11
create or replace view BeerInfo(beer, brewery, style, year, abv)
as
select b1.name, b2.name, s.name, brewed, abv
from beers b1, breweries b2, brewed_by r, styles s
where b1.id = r.beer
and b2.id = r.brewery
and b1.style = s.id
;

-- For Q10
create or replace function
	q10WithDup(_style text) returns setof BeerInfo
as $$
declare
    iter BeerInfo;
    res BeerInfo;
    collabBeer BeerInfo;
    collabBreweries text := '';
begin
    for iter in (
        select *
        from BeerInfo
        where _style = style
    )
    loop
        collabBreweries := '';
        if iter.beer in (
            select *
            from Q2
        )
        then
            for collabBeer in (
                select *
                from BeerInfo
                where _style = style
                and beer = iter.beer
                order by brewery
            )
            loop
                collabBreweries := collabBreweries || collabBeer.brewery || ' + ';
            end loop;
            collabBreweries = substring(collabBreweries from 1 for (char_length(collabBreweries) - 3));
        else
            collabBreweries := iter.brewery;
        end if;
        res.beer := iter.beer;
        res.brewery := collabBreweries;
        res.style := iter.style;
        res.year := iter.year;
        res.abv := iter.abv;
        return next res;
    end loop;
end;
$$
language plpgsql;

-- For Q11
create or replace function
	q11WithDup(partial_name text) returns setof text
as $$
declare
    iter BeerInfo;
    res text;
    collabBeer BeerInfo;
    collabBreweries text := '';
begin
    for iter in (
        select *
        from BeerInfo
        where beer like '%' || partial_name || '%'
        or beer like '%' || initcap(partial_name) || '%'
    )
    loop
        collabBreweries := '';
        if iter.beer in (
            select *
            from Q2
        )
        then
            for collabBeer in (
                select *
                from BeerInfo
                where beer = iter.beer
                order by brewery
            )
            loop
                collabBreweries := collabBreweries || collabBeer.brewery || ' + ';
            end loop;
            collabBreweries = substring(collabBreweries from 1 for (char_length(collabBreweries) - 3));
        else
            collabBreweries := iter.brewery;
        end if;
        res = '"' || iter.beer || '"';
        res = res || ', ' || collabBreweries;
        res = res || ', ' || iter.style;
        res = res || ', ' || iter.abv || '% ABV';
        return next res;
    end loop;
end;
$$
language plpgsql;

-- Q1: oldest brewery

create or replace view Q1(brewery)
as
select name
from breweries
where founded = 
(select min(founded) from breweries)
;

-- Q2: collaboration beers

create or replace view Q2(beer)
as
select name
from beers, brewed_by
where id = beer
group by id
having count(*) > 1
order by name
;

-- Q3: worst beer

create or replace view Q3(worst)
as
select name
from beers
where rating = 
(
	select min(rating)
	from beers
)
;

-- Q4: too strong beer

create or replace view Q4(beer,abv,style,max_abv)
as
select b.name, b.abv, s.name, s.max_abv
from beers b, styles s
where b.style = s.id and b.abv > s.max_abv
;

-- Q5: most common style

create or replace view Q5(style)
as
select style
from styleCount
where num = 
(
    select max(num) from styleCount
)
;

-- Q6: duplicated style names

create or replace view Q6(style1,style2)
as
select s1.name, s2.name
from styles s1, styles s2
where upper(s1.name) = upper(s2.name)
and s1.name < s2.name
;

-- Q7: breweries that make no beers

create or replace view Q7(brewery)
as
select name
from breweries
where id not in (
    select brewery
    from brewed_by
)
;

-- Q8: city with the most breweries

create or replace view Q8(city,country)
as
select distinct metro, country
from mostBreweries join locations
on city = metro
and num = (
    select max(num)
    from mostBreweries
)
;

-- Q9: breweries that make more than 5 styles

create or replace view Q9(brewery,nstyles)
as
select b2.name, count(distinct b1.style)
from beers b1, brewed_by r, breweries b2
where b1.id = r.beer
and b2.id = r.brewery
group by b2.name
having count(distinct b1.style) > 5
order by b2.name
;

-- Q10: beers of a certain style

create or replace function
	q10(_style text) returns setof BeerInfo
as $$
declare
    res BeerInfo;
begin
    for res in(
    select distinct *
    from q10WithDup(_style)
    order by beer
    )
    loop
        return next res;
    end loop;
end;
$$
language plpgsql;

-- Q11: beers with names matching a pattern

create or replace function
	Q11(partial_name text) returns setof text
as $$
declare
    res text;
begin
    for res in(
    select distinct *
    from q11WithDup(partial_name)
    order by q11withdup
    )
    loop
        return next res;
    end loop;
end;
$$
language plpgsql;

-- Q12: breweries and the beers they make

create or replace function
	q12(partial_name text) returns setof text
as $$
declare
    iter breweries;
    res text;
    resLocation text;
    loc locations;
    resBeer text;
    brewed_beers BeerInfo;
begin
    for iter in (
        select *
        from breweries
        where name like '%' || partial_name || '%'
        or name like '%' || initcap(partial_name) || '%'
        order by name
    )
    loop
        res := iter.name ||  ', ';
        res := res || 'founded ' || iter.founded;
        return next res;

        resLocation := '';
        for loc in (
            select *
            from locations
            where iter.located_in = id
        )
        loop
            if loc.town <> ''
            then
                resLocation := loc.town || ', ';

            elsif loc.metro <> ''
            then
                resLocation := loc.metro || ', ';
            end if;

            if loc.region <> ''
            then
                resLocation := resLocation || loc.region || ', ';
            end if;

            resLocation := resLocation || loc.country;
        end loop;
        
        res := 'located in ' || resLocation;
        return next res;

        resBeer := '';
        if iter.name in (
            select *
            from Q7
        )
        then
            resBeer := '  No known beers';
        else
            for brewed_beers in (
                select *
                from BeerInfo
                where brewery = iter.name
                order by year, beer
            )
            loop
                resBeer := '  ' || '"' || brewed_beers.beer || '"' || ', ';
                resBeer := resBeer || brewed_beers.style || ', ';
                resBeer := resBeer || brewed_beers.year || ', ';
                resBeer := resBeer || brewed_beers.abv || '% ABV';
                res := resBeer;
                return next res;
            end loop;
        end if;
    end loop;
end;
$$
language plpgsql;
