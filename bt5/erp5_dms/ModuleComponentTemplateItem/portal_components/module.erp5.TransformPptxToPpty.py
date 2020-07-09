from Products.PortalTransforms.interfaces import itransform
from zope.interface import implements
from erp5.component.module.OOOdCommandTransform import OOOdCommandTransform, OOoDocumentDataStream

class PptxToPpty:
  """Transforms pptx to ppty by using Cloudooo"""

  implements(itransform)

  __name__ = 'pptx_to_ppty'
  inputs   = ('application/vnd.openxmlformats-officedocument.presentationml.presentation',)
  output = 'application/x-asc-presentation'

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
    pptx = OOOdCommandTransform(context, filename, data, self.inputs[0])
    ppty = pptx.convertTo('ppty')
    if cache is not None:
      cache.setData(ppty)
      return cache
    else:
      stream = OOoDocumentDataStream()
      stream.setData(ppty)
      return stream

def register():
  return PptxToPpty()
