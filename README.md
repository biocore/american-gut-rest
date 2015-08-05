# american-gut-rest

A RESTful(ish) interface into the unidentified American Gut data. Any invalid response, or a query requesting an unknown sample will return a 410 HTTP status. 

# Endpoints

| endpoint | description | example | result | 
| :------- | ----------- | ------- | -----: |
| `GET /`    | Endpoint detail | `curl https://api.microbio.me/american-gut/1/` | `{"foo_url": ...}`
| `GET /otu/:sample-id` | A sample specific OTU table | `curl https://api.microbio.me/american-gut/1/otu/000005636.1053788` | A [BIOM-format 1.0.0](http://biom-format.org/documentation/format_versions/biom-1.0.html) table |
| `GET /otu/:sample-id/txt` | A sample specific Excel OTU table | `curl https://api.microbio.me/american-gut/1/otu/000005636.1053788/txt` | A tab delimited string |
| `GET /otu/:sample-id/json` | A sample specific OTU table | `curl https://api.microbio.me/american-gut/1/otu/000005636.1053788/json` | A [BIOM-format 1.0.0](http://biom-format.org/documentation/format_versions/biom-1.0.html) table |
| `GET /sample` | A list of the known samples | `curl https://api.microbio.me/american-gut/1/sample/` | `["foo", "bar", ...]`
| `GET /sequence/:sample-id` | Per-sample sequences for download | `curl https://api.microbio.me/american-gut/1/sequence/000005636.1053788` | `{"fastq_url": "ftp://..."}` |


