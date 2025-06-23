from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from collections import OrderedDict


class TwitterCursorPagination(CursorPagination):
    page_size = 20
    page_size_query_param = 'pageSize'
    max_page_size = 100
    ordering = '-created_at'
    cursor_query_param = 'cursor'
    
    def get_paginated_response(self, data):
        next_cursor = None
        if self.has_next:
            next_cursor = self.get_next_link()
            if next_cursor:
                # Extract cursor from URL
                cursor_start = next_cursor.find('cursor=')
                if cursor_start != -1:
                    cursor_start += 7  # length of 'cursor='
                    cursor_end = next_cursor.find('&', cursor_start)
                    if cursor_end == -1:
                        cursor_end = len(next_cursor)
                    next_cursor = next_cursor[cursor_start:cursor_end]
                    
        return Response(OrderedDict([
            ('tweets', data),
            ('has_next_page', self.has_next),
            ('next_cursor', next_cursor),
            ('status', 'success'),
            ('msg', 'success')
        ]))


class TwitterFollowersPagination(CursorPagination):
    page_size = 20
    page_size_query_param = 'pageSize' 
    max_page_size = 100
    ordering = '-created_at'
    cursor_query_param = 'cursor'
    
    def get_paginated_response(self, data, data_key='followers'):
        next_cursor = None
        if self.has_next:
            next_cursor = self.get_next_link()
            if next_cursor:
                cursor_start = next_cursor.find('cursor=')
                if cursor_start != -1:
                    cursor_start += 7
                    cursor_end = next_cursor.find('&', cursor_start)
                    if cursor_end == -1:
                        cursor_end = len(next_cursor)
                    next_cursor = next_cursor[cursor_start:cursor_end]
                    
        return Response(OrderedDict([
            (data_key, data),
            ('has_next_page', self.has_next),
            ('next_cursor', next_cursor),
            ('status', 'success'),
            ('msg', 'success'),
            ('code', 0)
        ]))


class TwitterUserTweetsPagination(CursorPagination):
    page_size = 20
    page_size_query_param = 'pageSize'
    max_page_size = 100
    ordering = '-created_at'
    cursor_query_param = 'cursor'
    
    def get_paginated_response(self, data):
        next_cursor = None
        if self.has_next:
            next_cursor = self.get_next_link()
            if next_cursor:
                cursor_start = next_cursor.find('cursor=')
                if cursor_start != -1:
                    cursor_start += 7
                    cursor_end = next_cursor.find('&', cursor_start)
                    if cursor_end == -1:
                        cursor_end = len(next_cursor)
                    next_cursor = next_cursor[cursor_start:cursor_end]
                    
        return Response(OrderedDict([
            ('status', 'success'),
            ('code', 0),
            ('msg', 'success'),
            ('data', {
                'pin_tweet': None,
                'tweets': data
            }),
            ('has_next_page', self.has_next),
            ('next_cursor', next_cursor)
        ]))