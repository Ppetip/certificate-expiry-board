"""Prioritize exported certificate inventories by expiry and not-before dates using an explicit reproducible clock."""
from datetime import datetime, timezone
import math

def stamp(value):
    result = datetime.fromisoformat(value.replace('Z','+00:00'))
    if result.tzinfo is None:
        raise ValueError('timezone required')
    return result.astimezone(timezone.utc)

def analyze(data):
    now = stamp(data['now'])
    warning = int(data.get('warning_days',30))
    if warning<0:
        raise ValueError('warning_days must be nonnegative')
    result = []
    for cert in data['certificates']:
        start,end = stamp(cert['not_before']),stamp(cert['not_after'])
        if start >= end:
            raise ValueError('invalid certificate validity range')
        seconds = (end-now).total_seconds()
        kind = 'not_yet_valid' if now<start else 'expired' if seconds<=0 else 'expiring' if seconds<=warning*86400 else 'healthy'
        result.append(dict(kind=kind,name=cert['name'],days_remaining=math.floor(seconds/86400),not_after=cert['not_after']))
    return sorted(result,key=lambda x:(x['days_remaining'],x['name']))


def main():
    import argparse, json, sys
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='path to JSON input, or - for stdin')
    args = parser.parse_args()
    try:
        if args.input == '-':
            data = json.load(sys.stdin)
        else:
            with open(args.input, encoding='utf-8') as stream:
                data = json.load(stream)
        result = analyze(data)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (ValueError, KeyError, TypeError, OSError, OverflowError) as error:
        print('Invalid input: '+str(error), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
