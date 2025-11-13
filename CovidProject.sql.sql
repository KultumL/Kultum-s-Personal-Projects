USE Covid ;
-- Standardize Date Format

UPDATE covid.coviddeaths
SET date = STR_TO_DATE(date, '%c/%e/%y')
WHERE date LIKE '%/%';

UPDATE covid.CovidVaccinations
SET date = STR_TO_DATE(date, '%c/%e/%y')
WHERE date LIKE '%/%';

-- Update missing Null values for Continent 

UPDATE covid.coviddeaths
set continent = null
where continent = '' ;

UPDATE covid.CovidVaccinations
set continent = null
where continent = '' ;

-- Covid 19 Data Exploration 

SELECT * 
FROM covid.CovidDeaths
WHERE continent is not null
ORDER BY location , date;

-- Data to focus on

SELECT location, date, total_cases, new_cases, total_deaths, population
FROM covid.CovidDeaths
WHERE continent is not null
ORDER BY location, date;

-- Total cases vs Total Deaths
-- Shows likelihood of dying if you contract covid in your country
-- Focus on the United States

SELECT location, date,total_cases,total_deaths, (total_deaths/total_cases)* 100 as DeathPercentage 
FROM covid.CovidDeaths
WHERE location like '%states%' AND continent is not null
ORDER BY location, date;

-- Looking at Total Cases vs Population
-- Shows what percentage of population infected with covid

SELECT location, date,total_cases,total_deaths, (total_cases/population)*100 as PercentPopulationInfected
FROM covid.CovidDeaths
WHERE location like '%states%' 
ORDER BY location, date;

-- Looking at counties with Highest Infection Rate compared to Population

SELECT location,population, MAX(total_cases) as HighestInfectionCount, Max((total_cases/population))*100 as PercentPopulationInfected
FROM covid.CovidDeaths
-- where location like '%states%'
WHERE continent is not NULL
GROUP BY location, population
ORDER BY PercentPopulationInfected desc;

-- Showing countries with Highest Death Count per population

SELECT location,population, MAX(total_deaths) as TotalDeathCount
FROM covid.CovidDeaths
WHERE continent is not NULL
GROUP BY location
ORDER BY TotalDeathCount desc;

-- Focuing on Continents 


-- Showing continents with highest death count per population

SELECT location,population, MAX(total_deaths) as TotalDeathCount
FROM covid.CovidDeaths
WHERE continent is not NULL
GROUP BY continent 
ORDER BY TotalDeathCount desc;

-- death rate, GLOBAL NUMBERS

SELECT SUM(new_cases)as total_cases , SUM(new_deaths) as total_deaths , SUM(new_deaths)/sum(new_cases) *100 as DeathPercentag
FROM covid.CovidDeaths
WHERE continent is not NULL
ORDER BY total_cases, total_deaths ;

-- Total Population vs Vaccinations
-- Shows Percentage of Population that has recieved at least one Covid Vaccine

Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, SUM(vac.new_vaccinations) OVER (Partition by dea.Location Order by dea.location, dea.Date) as RollingPeopleVaccinated
From covid.CovidDeaths dea
Join covid.CovidVaccinations vac
	On dea.location = vac.location
	and dea.date = vac.date
where dea.continent is not null 
order by dea.location,dea.date

-- Using CTE to perform Calculation on Partition By in previous query

With PopvsVac (Continent, Location, Date, Population, New_Vaccinations, RollingPeopleVaccinated)AS  
(
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations
, SUM(vac.new_vaccinations) OVER (Partition by dea.Location Order by dea.location, dea.Date) as RollingPeopleVaccinated
FROM covid.CovidDeaths dea JOIN covid.CovidVaccinations vac
	ON dea.location = vac.location
	AND dea.date = vac.date
WHERE  dea.continent is not null
)
Select *, (RollingPeopleVaccinated/Population)*100
From PopvsVac



-- Using Temp Table to perform Calculation on Partition By in previous query

DROP Table if exists PercentPopulationVaccinated;
Create Table PercentPopulationVaccinated
(
Continent varchar(255),
Location varchar(255),
Date datetime,
Population numeric,
New_vaccinations numeric,
RollingPeopleVaccinated numeric
);

Insert into PercentPopulationVaccinated(
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations
, SUM(vac.new_vaccinations) OVER (Partition by dea.Location Order by dea.location, dea.Date) as RollingPeopleVaccinated
From covid.CovidDeaths dea
Join covid.CovidVaccinations vac
	On dea.location = vac.location
	and dea.date = vac.date
)

Select *, (RollingPeopleVaccinated/Population)*100
From PercentPopulationVaccinated




-- Creating View to store data for later visualizations

CREATE VIEW PercentPopulationVaccinated as
SELECT dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations
, SUM(vac.new_vaccinations) OVER (PARTITION BY dea.Location ORDER BY dea.location, dea.Date) as RollingPeopleVaccinated
FROM covid.CovidDeaths dea JOIN covid.CovidVaccinations vac
	ON dea.location = vac.location
	AND dea.date = vac.date
WHERE  dea.continent is not null

