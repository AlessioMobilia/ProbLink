#!/usr/bin/env python
import datetime
import argparse
from _pybgpstream import BGPStream, BGPRecord
# Log every 1000 paths.
LOG_EVERY_N = 10000


def downloader(start_date, duration):
    """Download BGP paths from Routeviews and RIPE NCC from a start date for a certain duration."""

    # Start of UNIX time
    base = int(datetime.datetime.strptime(start_date, '%m/%d/%Y').strftime('%s'))
    # Create a new bgpstream instance and a reusable bgprecord instance
    stream = BGPStream()
    stream.add_interval_filter(base, base + int(duration))
    stream.add_filter('record-type', 'ribs')
    stream.add_interval_filter(base, base + int(duration))
    stream.start()
    print('Downloading BGP paths:')
    path_set = set()
    f = open('rib.txt', 'w')
    count=0
    print('Downloading Paths...')


    while True:
        count +=1
        if (count % LOG_EVERY_N) == 0:
            print('records:'+str(count), end='\r')
        rec = stream.get_next_record()
        if rec is None:
            print('Paths Downloaded')
            return
        if rec.status != "valid":
            continue
        else:
            elem = rec.get_next_elem()
            while(elem):
                path = elem.fields['as-path']
                if '{' in path or '(' in path:
                    elem = rec.get_next_elem()
                    continue
                prefix = elem.fields['prefix']
                # Focus on IPv4 prefixes
                if ":" not in prefix and path not in path_set:
                    f.write(path.replace(' ', '|') + '\n')
                    path_set.add(path)
                elem = rec.get_next_elem()
    f.close()
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download BGP paths from a start date for a duration')
    parser.add_argument('-s', '--start',
                        help='The start date',
                        required=True)
    parser.add_argument('-d', '--duration',
                        help='Duration in minutes',
                        required=True)
    args = parser.parse_args()
    downloader(args.start, args.duration)
