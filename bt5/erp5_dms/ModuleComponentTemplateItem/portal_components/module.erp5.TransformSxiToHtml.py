from Products.PortalTransforms.interfaces import itransform
from zope.interface import implements
from erp5.component.module.OOOdCommandTransform import OOOdCommandTransform, OOoDocumentDataStream


class SxiToHtml:
  """Transforms sxi to html by using Cloudooo"""

  implements(itransform)

  __name__ = 'sxi_to_html'
  inputs   = ('application/vnd.sun.xml.impress',)
  output = 'text/html'

  tranform_engine = OOOdCommandTransform.__module__

  def name(self):
    return self.__name__

  def __getattr__(self, attr):
    if attr == 'inputs':
      return self.config['inputs']
    if attr == 'output':
      return self.config['output']
    raise AttributeError(attr)

  def convert(self, orig, data, cache=None, filename=None, context=None, **kwargs):
    data = str(orig)
    sxi = OOOdCommandTransform(context, filename, data, self.inputs[0])
    html = sxi.convertTo('html')
    if cache is not None:
      cache.setData(html)
      return cache
    else:
      stream = OOoDocumentDataStream()
      stream.setData(html)
      return stream

def register():
  return SxiToHtml()
