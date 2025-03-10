import { NextResponse, NextRequest } from "next/server";
import { DEFAULT_MODEL, sunoApi } from "@/lib/SunoApi";
import { corsHeaders } from "@/lib/utils";

export const dynamic = "force-dynamic";



/**
 * desc
 *
 */
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
  
    let userMessage = null;
    const { messages } = body;
    for (let message of messages) {
      if (message.role == 'user') {
        userMessage = message;
      }
    }
  
    if (!userMessage) {
      return new NextResponse(JSON.stringify({ error: 'Prompt message is required' }), {
        status: 400,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }
  
    // Log before the API call
    console.log("Before API call:", {
      userMessage: userMessage.content,
      model: DEFAULT_MODEL,
      otherParams: {
        shouldIncludeLyrics: true,
        shouldIncludeMetadata: true,
      },
    });
  
    const testAudioInfo = await (await sunoApi()).generate("Test prompt", true, DEFAULT_MODEL, true);
    console.log("Test Audio Info:", testAudioInfo);
    const audioInfo = await (await sunoApi()).generate(userMessage.content, true, DEFAULT_MODEL, true);
  
    // Log after the API call
    console.log("After API call:", audioInfo);
  
    if (!audioInfo || !Array.isArray(audioInfo) || audioInfo.length === 0) {
      return new NextResponse(
        JSON.stringify({ error: "No audio data received from the API" }),
        {
          status: 500,
          headers: {
            'Content-Type': 'application/json',
            ...corsHeaders
          }
        }
      );
    }
  
    const audio = audioInfo[0];
    const data = `## Song Title: ${audio.title}\n![Song Cover](${audio.image_url})\n### Lyrics:\n${audio.lyric}\n### Listen to the song: ${audio.audio_url}`;
  
    return new NextResponse(data, {
      status: 200,
      headers: corsHeaders
    });
  } catch (error: any) {
    console.error('Error generating audio:', error); // Log the full error for debugging
  
    let errorMessage = "Unknown error occurred";
    if (error.response?.data) {
      errorMessage = typeof error.response.data === "object" 
        ? JSON.stringify(error.response.data) 
        : error.response.data;
    } else if (error.message) {
      errorMessage = error.message;
    }
  
    return new NextResponse(
      JSON.stringify({ error: `Internal server error: ${errorMessage}` }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      }
    );
  }


export async function OPTIONS(request: Request) {
  return new Response(null, {
    status: 200,
    headers: corsHeaders
  });
}