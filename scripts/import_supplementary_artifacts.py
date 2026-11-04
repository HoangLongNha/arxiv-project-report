"""Preserve the two newly supplied TV4 sessions without replacing earlier evidence."""
import import_member_artifacts as importer

importer.DEST = importer.ROOT / 'summaries/milestone1/supplementary-20261104'
importer.SOURCES = {
    'TV4-20261101': ('tv4-nov01-artifacts.zip', '1Ty_QGkCTR6Q0tsbkA68ZMr941-163L-5'),
    'TV4-20261102': ('tv4-nov02-artifacts.zip', '1lTMZXs74FKNp8iH0pmA-bk1nyxH56F2x'),
}
if __name__ == '__main__':
    importer.main()
