/**
 * Home page
 *
 * Upload script directly with quick syntax reference
 */

import { Link } from 'react-router-dom'
import { ScriptUpload } from '../components/ScriptUpload'
import type { UploadResponse } from '../types/models'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'

export function Home() {

  const navigate = useNavigate()



  const handleUploadSuccess = (data: UploadResponse) => {

    navigate('/workflow', { state: { initialStep: 'review', uploadData: data } })

  }



  return (

    <div className="min-h-screen relative overflow-hidden flex flex-col items-center justify-center p-4 bg-[#0a0a0a]">

      {/* Editorial Filmic Background */}

      <div className="fixed inset-0 z-0 pointer-events-none">

        <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')]" />

        

        {/* Mesh Gradient 1: Deep Blue/Violet */}
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            x: ['-10%', '10%', '-5%'],
            y: ['-10%', '5%', '-10%']
          }}
          transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-0 left-0 w-[80vw] h-[80vh] rounded-full filter blur-[100px] opacity-20"
          style={{ backgroundColor: '#4f46e5' }}
        />

        {/* Mesh Gradient 2: Cyan/Teal */}
        <motion.div
          animate={{
            scale: [1.1, 0.9, 1.2],
            x: ['10%', '-15%', '10%'],
            y: ['10%', '20%', '10%']
          }}
          transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-0 right-0 w-[90vw] h-[90vh] rounded-full filter blur-[120px] opacity-20"
          style={{ backgroundColor: '#0891b2' }}
        />

        {/* Mesh Gradient 3: Accent Purple/Orange */}
        <motion.div
          animate={{
            scale: [0.9, 1.3, 1],
            x: ['20%', '-10%', '20%'],
            y: ['-20%', '10%', '-20%']
          }}
          transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-1/4 right-0 w-[50vw] h-[50vh] rounded-full filter blur-[100px] opacity-20"
          style={{ backgroundColor: '#7c3aed' }}
        />

        

        <div className="absolute bottom-0 left-0 w-full h-1/2 bg-gradient-to-t from-black to-transparent opacity-60" />

      </div>



            <motion.div 



              initial={{ opacity: 0, y: 20 }}



              animate={{ opacity: 1, y: 0 }}



              transition={{ duration: 1.6, ease: [0.16, 1, 0.3, 1] }}



              className="w-full max-w-4xl relative z-10"



            >



      

        <div className="space-y-24">

          {/* Editorial Header */}

          <div className="space-y-8">

            <div className="flex flex-col items-center">

              <motion.div

                initial={{ opacity: 0, scale: 0.9 }}

                animate={{ opacity: 1, scale: 1 }}

                transition={{ duration: 1, delay: 0.2 }}

                className="mb-8"

              >

                <div className="px-3 py-1 border border-white/10 rounded-full bg-white/5 backdrop-blur-sm">

                  <span className="text-[10px] font-black text-white/40 uppercase tracking-[0.4em]">Director's Suite v1.0</span>

                </div>

              </motion.div>

              

              <h1 

                className="text-7xl md:text-9xl font-medium tracking-tight text-white leading-[0.85] text-center"

                style={{ fontFamily: "'Charter', 'Bitstream Charter', 'Sitka Text', Cambria, serif" }}

              >

                Screen<span className="italic font-normal text-blue-500 transform inline-block">Write</span>

              </h1>

              

              <p className="mt-8 text-lg md:text-xl text-white/40 font-medium tracking-wide text-center max-w-lg mx-auto leading-relaxed">

                Transform scripts into timelines. <br />

                The professional way to manage B-roll.

              </p>

            </div>

          </div>



          {/* Primary Action Card */}

          <motion.div

            initial={{ opacity: 0, y: 30 }}

            animate={{ opacity: 1, y: 0 }}

            transition={{ duration: 1, delay: 0.6, ease: [0.16, 1, 0.3, 1] }}

            className="max-w-2xl mx-auto w-full"

          >

                        <div className="bg-white/[0.02] backdrop-blur-3xl border border-white/5 shadow-[0_48px_96px_-24px_rgba(0,0,0,0.5)] rounded-[32px] overflow-hidden">

                           <div className="p-1">

                             <div className="bg-black/40 rounded-[30px] p-8 md:p-12">

                               <ScriptUpload onUploadSuccess={handleUploadSuccess} />

                             </div>

                           </div>

                        </div>

          </motion.div>



          {/* Minimal Footer */}

          <motion.div 

            initial={{ opacity: 0 }}

            animate={{ opacity: 1 }}

            transition={{ duration: 1, delay: 1 }}

            className="flex flex-col items-center gap-8"

          >

            <Link 

              to="/syntax-guide" 

              className="group flex items-center gap-4 text-white/30 hover:text-white transition-colors duration-500"

            >

              <span className="text-[10px] font-black uppercase tracking-[0.3em]">Explore the Syntax</span>

              <div className="w-12 h-px bg-white/10 group-hover:w-24 group-hover:bg-blue-500 transition-all duration-700" />

            </Link>

          </motion.div>

        </div>

      </motion.div>

    </div>

  )

}
