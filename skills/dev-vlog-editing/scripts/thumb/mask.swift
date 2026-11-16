// Person mask for a photo, using macOS's built-in Vision person segmentation. Usage: swift mask.swift in.jpg mask.png
import Foundation
import Vision
import CoreImage
import ImageIO
import UniformTypeIdentifiers

let args = CommandLine.arguments
let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: args[1]) as CFURL, nil)!
let image = CGImageSourceCreateImageAtIndex(src, 0, nil)!
let request = VNGeneratePersonSegmentationRequest()
request.qualityLevel = .accurate
request.outputPixelFormat = kCVPixelFormatType_OneComponent8
try VNImageRequestHandler(cgImage: image, options: [:]).perform([request])
let buffer = request.results!.first!.pixelBuffer
let ci = CIImage(cvPixelBuffer: buffer)
let out = CIContext().createCGImage(ci, from: ci.extent)!
let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: args[2]) as CFURL, UTType.png.identifier as CFString, 1, nil)!
CGImageDestinationAddImage(dest, out, nil)
CGImageDestinationFinalize(dest)
print("mask", out.width, out.height)
