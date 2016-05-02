# Timeline Scraper
Timeline Scraper is designed to provide an extensible infrastructure for continuous scraping of temporal data, i.e. data that varies over time, here referred as timelines.

The scraper main source code is in *TimelineScraper.py* and is a python implementation of an algorithm that fetches 
twitter data using its search API. See "Working with Timelines" tutorial at [twitter_timelines] for more details.

In the *engines* forlder there are specific implementations of the TimelineScraperEngine interface.
The first implementation is built to fetch tweets that correspond to particular keywords, using Twitter search API.
See "Extending TimelineScraper with new Engines" section.

*TimelineScraperManager.py* and the *web* folder contain, respectively, the backend and frontend of a web application
that can be used to easily control and monitor timeline scrapers. The backend is built with [flask], while the frontend uses
[polymer].

## How to run scrapers using the manager

1. Clone or download this repo
2. Run ```python TimelineScraperManager.py```
3. Visit ```http://localhost:5048```
4. Insert username=admin and password=password to log into the control panel

## How to extend TimelineScraper with new Engines
TimelineCrawler can be extended by implementing a subclass of engines/TimelineCrawlerEngine.py
See inline documentation for more information.

It's then necessary to add the new engine to the TimelineCrawlerManager, by importing the new engine and linking
it in the engines global vartiable.

## How to extend TimelineScraper with new ResultsStore
Scraped data is currently stored in the file system, but you can create your own connector to other kind of data stores.
*TODO*

## References
[twitter_timelines]: https://dev.twitter.com/rest/public/timelines "Twitter timelines"
[flask]: http://flask.pocoo.org/ "Flask"
[polymer]: https://www.polymer-project.org/1.0/ "Polymer"
