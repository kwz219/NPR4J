/*
 *  Igapyon Diary system v3 (IgapyonV3).
 *  Copyright (C) 2015-2017  Toshiki Iga
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU Lesser General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU Lesser General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
/*
 *  Copyright 2015-2017 Toshiki Iga
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

package jp.igapyon.diary.v3.gendiary;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.io.FileUtils;

import jp.igapyon.diary.v3.util.IgapyonV3Settings;

/**
 * 今日付けの日記ファイル igyyMMdd.html.src.md を生成するクラス。
 * 
 * ファイルが存在しなければこれを新規作成します。
 * 
 * @author Toshiki Iga
 */
public class TodayDiaryGenerator {
	private IgapyonV3Settings settings = null;

	public TodayDiaryGenerator(final IgapyonV3Settings settings) {
		this.settings = settings;
	}

	/**
	 * 主たるエントリーポイント。
	 * 
	 * @param rootdir
	 * @throws IOException
	 */
	public void processDir() throws IOException {
		final File yearDir = getYearDir();

		// ファイル名は igyyMMdd.html.src.md 形式。
		final File file = getTodayDiaryFile(yearDir);
		if (file.exists()) {
			// すでに本日の日記ファイルは存在します。処理中断します。
			System.err.println("Today's diary is alread exist.: " + file.getAbsolutePath());
			return;
		}

		// 日記ファイルの新規作成に移ります。

		final List<String> lines = new ArrayList<String>();
		lines.add("## ここにコンテンツのタイトル");
		lines.add("");
		lines.add("ここに何か内容。");
		lines.add("");
		lines.add("* 箇条書き1");
		lines.add("* 箇条書き2");
		lines.add("  * 箇条書き2-1");
		lines.add("");
		lines.add("```java");
		lines.add("System.out.println(\"Hello world\");");
		lines.add("```");
		lines.add("");
		lines.add("<#-- copyright " + settings.getAuthor() + " -->");
		lines.add("<@linkshare word=\"本日の日記。ここに日記タイトルが入ってほしい。\"/>");

		// 日記ファイルを新規作成します。
		FileUtils.writeLines(file, lines);
		System.err.println("Today's diary md file was created: " + file.getAbsolutePath());
	}

	/**
	 * 本日の日記ファイルを取得します。
	 * 
	 * @param yearDir
	 * @return
	 */
	protected File getTodayDiaryFile(final File yearDir) {
		// ファイル名は igyyMMdd.html.src.md 形式。
		final String yymmdd = new SimpleDateFormat("yyMMdd").format(settings.getToday());
		return new File(yearDir, ("ig" + yymmdd + ".html.src.md"));
	}

	/**
	 * 日記システムの今日の日記のためのルートディレクトリを取得します。
	 * 
	 * ディレクトリが存在しない場合は新規作成します。
	 * 
	 * @param rootdir
	 * @return
	 * @throws IOException
	 */
	protected File getYearDir() throws IOException {
		final String yyyy = new SimpleDateFormat("yyyy").format(settings.getToday());
		final File yearDir = new File(settings.getRootdir(), yyyy);
		if (yearDir.exists() == false) {
			if (yearDir.mkdirs() == false) {
				throw new IOException("Fail to create 'year' dir [" + yearDir.getCanonicalPath() + "]. End process.");
			}
			System.err.println("New Year dir was created: " + yearDir.getAbsolutePath());
		}

		return yearDir;
	}

	/**
	 * テスト用のエントリポイント。
	 * 
	 * @param args
	 * @throws IOException
	 */
	public static void main(String[] args) throws IOException {
		File dir = new File(".");
		dir = dir.getCanonicalFile();

		if (dir.getName().equals("igapyonv3")) {
			final IgapyonV3Settings settings = new IgapyonV3Settings();
			new TodayDiaryGenerator(settings).processDir();
		} else {
			System.out.println("期待とは違うディレクトリ:" + dir.getName());
			return;
		}
	}
}
