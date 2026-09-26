/** Shared RePKG file-type checks used by both the trusted backend and renderer UI. */

const packagePattern = /\.(?:pkg|mpkg)$/i;
const imagePattern = /\.(?:png|jpe?g|gif|webp|bmp|avif)$/i;

export const isRepkgPackage = (filePath: string): boolean => packagePattern.test(filePath.trim());
export const isPreviewImage = (filePath: string): boolean => imagePattern.test(filePath.trim());
export const displayFileName = (filePath: string): string => filePath.split(/[\\/]/).pop() || filePath;
export const sortRepkgOutput = (files: string[]): string[] => [...files].sort((left, right) => Number(isPreviewImage(right)) - Number(isPreviewImage(left)) || left.localeCompare(right));
