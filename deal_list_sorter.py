class DealListSorter(object):
    def sort_deals(self,deals):
        for deal in deals:
            try:
                deal['expected_value'] = deal.get('value') * deal.get('probability') / 100
            except:
                deal['expected_value'] = deal.get('value')
        sorted_deals = sorted(deals, key=lambda k: k['expected_value'], reverse=True)
        return (sorted_deals)