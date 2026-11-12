"""Import corrected TV3/TV4 evidence without replacing earlier snapshots."""
import import_member_artifacts as importer

importer.DEST = importer.ROOT / 'summaries/milestone1/updated-20261106'
importer.CHECKED_ON = '2026-11-06'
importer.NOTE = 'Downloaded corrected archive from the shared Drive; original ZIP and earlier snapshots preserved.'
importer.SOURCES = {
    'TV3': ('tv3-updated-20261106.zip', '1_EHFFbJiWyfmUHwI-CHrVvxINXCFiSoT'),
    'TV4': ('tv4-nov01-updated-20261106.zip', '1djrLWYgC2Ck-y9GfLZ-6sm9D8zDR8zm5'),
    'TV4-session-20261102': ('tv4-nov02-updated-20261106.zip', '1qcg2v43Lzp-8jvvUR2e9TeBZZPFgUXSo'),
}
importer.ARCHIVE_TITLES = {
    'TV3': 'TV_tv3_MS1_RESULTS_run_20261103T093027Z_d25e1342e7e5487385657eef35648a6c.zip',
    'TV4': 'TV_tv4_MS1_RESULTS_run_20261101T061837Z_c93066d96e6c499a992556f59190e689.zip',
    'TV4-session-20261102': 'TV_tv4_MS1_RESULTS_run_20261102T145325Z_c9c323fedf744580a333ef81579b04ef.zip',
}
if __name__ == '__main__':
    importer.main()
