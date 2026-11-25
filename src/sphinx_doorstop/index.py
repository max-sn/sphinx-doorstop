# class ItemIndex(Index):
#     name = "doorstopitem"
#     localname = "Doorstop items"
#     shortname = "Items"

#     def generate(self, docnames=None):

#         domain = cast(DoorstopDomain, self.domain)
#         content = defaultdict(list)

#         # Sort the items in alphabetical order
#         items = domain.get_items()
#         documents = domain.get_documents()

#         for item in items:
#             content[]

#         return sorted(content.items())
