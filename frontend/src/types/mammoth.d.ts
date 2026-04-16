// TypeScript declarations для mammoth.js
declare module 'mammoth' {
  export interface ConvertImageOptions {}
  
  export interface ConvertToHtmlResult {
    value: string;
    messages: any[];
  }

  export interface ConvertOptions {
    arrayBuffer: ArrayBuffer;
    image?: ConvertImageOptions;
  }

  export function convertToHtml(options: ConvertOptions): Promise<ConvertToHtmlResult>;
  export function convertToRaw(options: ConvertOptions): Promise<any>;
}
