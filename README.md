# WMATAscraper
Pull WMATA daily service reports from the archive.

The Washington Metropolitan Area Transit Authority (WMATA) maintains a [daily service report archive](http://wmata.com/rail/service_reports/viewReportArchive.cfm)
containing all service-related events by day.

This scraper retrieves the entirety of the service archive and parses it, producing timestamps
for each incident, and attempting to retrieve the following:

1. The cause of the incident.
2. The line on which the incident occurred.
3. The delay incurred, if any.
