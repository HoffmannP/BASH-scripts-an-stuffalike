BEGIN {
    FS=","
    OFS=";"
    days=0
    curr_continent="null"
    curr_location="null"
    total_new_cases_per_million=0
    max_people_fully_vaccinated_per_hundred=0
    print "continent","location","new_cases_per_week_per_100000","people_fully_vaccinated_per_hundred"
}
{
    continent=$2
    location=$3
    date=$4
    new_cases_per_million=$12
    people_fully_vaccinated_per_hundred=$43
    population=$49

    if (continent == "") {
        next
    }
    if (date !~ "2021-(11-[23]|12-0)") {
        next
    }
    if (population < 3000000) {
        next
    }

    if (curr_location != location) {
        if ((days >= 7) && (total_new_cases_per_million > 0) && (max_people_fully_vaccinated_per_hundred > 0)) {
            week_average_per_100000=7*total_new_cases_per_million/days/10
            print curr_continent,curr_location,week_average_per_100000,max_people_fully_vaccinated_per_hundred
        }
        days=0
        curr_continent=continent
        curr_location=location
        total_new_cases_per_million=0
        max_people_fully_vaccinated_per_hundred=0
    }
    if (new_cases_per_million > 0) {
        days+=1
        total_new_cases_per_million+=new_cases_per_million
    }
    if (people_fully_vaccinated_per_hundred > max_people_fully_vaccinated_per_hundred) {
        max_people_fully_vaccinated_per_hundred=people_fully_vaccinated_per_hundred
    }
}
END {
    if ((days >= 7) && (total_new_cases_per_million > 0) && (max_people_fully_vaccinated_per_hundred > 0)) {
        week_average_per_100000=7*total_new_cases_per_million/days/10
        print curr_continent,curr_location,week_average_per_100000,max_people_fully_vaccinated_per_hundred
    }
}
