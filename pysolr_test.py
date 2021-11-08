import pysolr
import json


solr_core = 'jim_core'
admin_core = 'admin'

# Tried creating a core per instance.
# Going to move that externally, as the SolrCoreAdmin functions are not working as I'd expect
# solr_admin = pysolr.SolrCoreAdmin('http://localhost:8983/solr/admin/cores')
# a = solr_admin.status(core=solr_core)
# a = json.loads(a)
#
# if solr_core in a['status']:
#     solr_admin.unload(solr_core)
#
# b = solr_admin.create(name=solr_core)
# b_json = json.loads(b)
#
# a = solr_admin.status(core=solr_core)
# a = json.loads(a)

# Create a client instance. The timeout and authentication options are not required.
solr = pysolr.Solr('http://localhost:8983/solr/'+solr_core, always_commit=True, timeout=10)

# Note that auto_commit defaults to False for performance. You can set
# `auto_commit=True` to have commands always update the index immediately, make
# an update call with `commit=True`, or use Solr's `autoCommit` / `commitWithin`
# to have your data be committed following a particular policy.

# Do a health check.
solr.ping()

# How you'd index data.
solr.add([
    {
        "id": "doc_1",
        "title": "A test document",
    },
    {
        "id": "doc_2",
        "title": "The Banana: Tasty or Dangerous?",
        "_doc": [
            { "id": "child_doc_1", "title": "peel" },
            { "id": "child_doc_2", "title": "seed" },
        ]
    },
])

# You can index a parent/child document relationship by
# associating a list of child documents with the special key '_doc'. This
# is helpful for queries that join together conditions on children and parent
# documents.

# Later, searching is easy. In the simple case, just a plain Lucene-style
# query is fine.
results = solr.search('title:"banana"')

# The ``Results`` object stores total results found, by default the top
# ten most relevant results and any additional data like
# facets/highlighting/spelling/etc.
print("Saw {0} result(s).".format(len(results)))

# Just loop over it to access the results.
for result in results:
    print("The title is '{0}'.".format(result['title']))

# # For a more advanced query, say involving highlighting, you can pass
# # additional options to Solr.
# results = solr.search('bananas', **{
#     'hl': 'true',
#     'hl.fragsize': 10,
# })
#
# # You can also perform More Like This searches, if your Solr is configured
# # correctly.
# similar = solr.more_like_this(q='id:doc_2', mltfl='text')
#
# # Finally, you can delete either individual documents,
# solr.delete(id='doc_1')
#
# # also in batches...
# solr.delete(id=['doc_1', 'doc_2'])
#
# # ...or all documents.
# solr.delete(q='*:*')
