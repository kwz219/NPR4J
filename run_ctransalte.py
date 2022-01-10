import ctranslate2

translator = ctranslate2.Translator("G:\\apimu\ctranslate", device="cpu")

# The OpenNMT-py and OpenNMT-tf models use a SentencePiece tokenization:
batch="java.util.List.size() java.util.ArrayList.init(int) <for_condition> java.util.List.size() </for_condition> <for_body> java.lang.String.valueOf(int) java.lang.System.currentTimeMillis() java.lang.Class.getSimpleName() </for_body>".split()
results=translator.translate_batch([batch])
print(results)
