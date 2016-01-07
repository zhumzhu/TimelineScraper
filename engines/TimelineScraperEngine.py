class TimelineScraperEngine(object):

    @property
    def timeline_scraper(self):
        return self.timeline_scraper

    @timeline_scraper.setter
    def timeline_scraper(self, timeline_scraper):
        self._timeline_scraper = timeline_scraper
        self.logger = timeline_scraper.logger
        self.logger.debug("Setting timeline_scraper property for engine")

    # Returns True or False
    def has_next(self):
        # could raise TimelineScraperError
        raise NotImplementedError("TimelineScraper.has_next should be implemented by subclasses!")

    # request_since is the last processed id
    # returns a list of results. Each result is a dict object
    # raises TimelineScraperRateLimitError
    # raises TimelineScraperError
    def get_next(self, request_since = None, request_to = None):
        raise NotImplementedError("TimelineScraper.get_next should be implemented by subclasses!")

    # Returns int
    def get_max_id_from_last_response(self):
        raise NotImplementedError("TimelineScraper.get_max_id_from_last_response should be implemented by subclasses!")

    # Returns int
    def get_min_id_from_last_response(self):
        raise NotImplementedError("TimelineScraper.get_min_id_from_last_response should be implemented by subclasses!")

    # Returns a unix timestamp
    def get_max_timestamp_from_last_response(self):
        raise NotImplementedError("TimelineScraper.get_max_timestamp_from_last_response should be implemented by subclasses!")

    # Returns a unix timestamp
    def get_min_timestamp_from_last_response(self):
        raise NotImplementedError("TimelineScraper.get_min_timestamp_from_last_response should be implemented by subclasses!")

    # Returns number of seconds
    def seconds_to_wait_after_timeline_exhausted(self):
        raise NotImplementedError("TimelineScraper.seconds_to_wait_after_timeline_exhausted should be implemented by subclasses!")

    def seconds_to_wait_after_rate_limit_exceeded(self):
        raise NotImplementedError("TimelineScraper.seconds_to_wait_after_rate_limit_exceeded should be implemented by subclasses!")